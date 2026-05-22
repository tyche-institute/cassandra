#!/usr/bin/env python3
"""Fetch public EU trusted-list snapshots for research observation.

This script records public XML bytes and provenance metadata. It does not
perform relying-party validation, supervision, or legal-status determination.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any
from urllib.parse import urlparse

import requests
from lxml import etree

LOTL_URL = "https://ec.europa.eu/tools/lotl/eu-lotl.xml"
USER_AGENT = "Tyche Institute Cassandra research monitor (contact: Anton Sokolov; research-only)"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_url(
    url: str,
    dest: pathlib.Path,
    timeout: int = 60,
    allow_error: bool = False,
) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/xml,text/xml,*/*;q=0.8"}
    started = now_iso()
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        content = response.content
        dest.write_bytes(content)
        meta = {
            "url": url,
            "accessed": started,
            "completed": now_iso(),
            "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "content_length_header": response.headers.get("Content-Length"),
            "bytes": len(content),
            "sha256": sha256_bytes(content),
            "destination": str(dest),
            "research_caveat": "Raw public XML snapshot for structural observation only; not relying-party validation or legal-status determination.",
        }
        write_json(dest.with_suffix(dest.suffix + ".meta.json"), meta)
        response.raise_for_status()
        return meta
    except requests.RequestException as exc:
        meta = {
            "url": url,
            "accessed": started,
            "completed": now_iso(),
            "http_status": None,
            "bytes": 0,
            "sha256": None,
            "destination": str(dest),
            "error": exc.__class__.__name__,
            "error_detail": str(exc),
            "research_caveat": "Fetch failure recorded for structural monitoring only; no legal-status inference is made.",
        }
        write_json(dest.with_suffix(dest.suffix + ".meta.json"), meta)
        if allow_error:
            return meta
        raise


def _text(el: etree._Element | None) -> str | None:
    if el is None or el.text is None:
        return None
    text = " ".join(el.text.split())
    return text or None


def extract_pointers(lotl_path: pathlib.Path) -> list[dict[str, str | None]]:
    parser = etree.XMLParser(resolve_entities=False, remove_blank_text=False, huge_tree=True)
    root = etree.parse(str(lotl_path), parser).getroot()
    ns = {"tsl": "http://uri.etsi.org/02231/v2#"}
    pointers: list[dict[str, str | None]] = []
    for pointer in root.xpath(".//tsl:PointersToOtherTSL/tsl:OtherTSLPointer", namespaces=ns):
        territory = _text(pointer.find(".//{http://uri.etsi.org/02231/v2#}SchemeTerritory"))
        location = _text(pointer.find(".//{http://uri.etsi.org/02231/v2#}TSLLocation"))
        mime = _text(pointer.find(".//{http://uri.etsi.org/02231/v2#}MimeType"))
        tsl_type = _text(pointer.find(".//{http://uri.etsi.org/02231/v2#}TSLType"))
        if location:
            pointers.append({
                "territory": territory,
                "url": location,
                "mime_type": mime,
                "tsl_type": tsl_type,
            })
    pointers.sort(key=lambda p: ((p.get("territory") or ""), (p.get("url") or "")))
    return pointers


def safe_name(territory: str | None, url: str, index: int) -> str:
    code = (territory or "unknown").strip().lower() or "unknown"
    code = "".join(ch if ch.isalnum() else "-" for ch in code).strip("-") or "unknown"
    suffix = pathlib.Path(urlparse(url).path).suffix or ".xml"
    return f"{index:02d}-{code}{suffix}"


def fetch_lotl(workspace: pathlib.Path) -> dict[str, Any]:
    return fetch_url(LOTL_URL, workspace / "sources" / "eu-lotl.xml")


def parse_lotl(workspace: pathlib.Path) -> list[dict[str, str | None]]:
    pointers = extract_pointers(workspace / "sources" / "eu-lotl.xml")
    write_json(workspace / "notes" / "pointers.json", {
        "created": now_iso(),
        "source": "sources/eu-lotl.xml",
        "count": len(pointers),
        "pointers": pointers,
        "research_caveat": "Pointers extracted for structural observation only.",
    })
    return pointers


def fetch_nationals(workspace: pathlib.Path, date: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    date = date or dt.date.today().isoformat()
    pointer_doc = json.loads((workspace / "notes" / "pointers.json").read_text(encoding="utf-8"))
    pointers = pointer_doc["pointers"]
    if limit is not None:
        pointers = pointers[:limit]
    metas = []
    for idx, pointer in enumerate(pointers, start=1):
        url = pointer["url"]
        assert url is not None
        dest = workspace / "snapshots" / date / safe_name(pointer.get("territory"), url, idx)
        meta = fetch_url(url, dest, allow_error=True)
        meta["territory"] = pointer.get("territory")
        metas.append(meta)
    ok_count = sum(1 for meta in metas if not meta.get("error"))
    error_count = len(metas) - ok_count
    write_json(workspace / "snapshots" / date / "manifest.json", {
        "created": now_iso(),
        "date": date,
        "count": len(metas),
        "ok_count": ok_count,
        "error_count": error_count,
        "items": metas,
        "research_caveat": "Public XML snapshots for structural observation only; not legal-status determination. Fetch failures are operational observations, not status claims.",
    })
    return metas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["lotl", "pointers", "nationals"])
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    if args.command == "lotl":
        print(json.dumps(fetch_lotl(workspace), indent=2, sort_keys=True))
    elif args.command == "pointers":
        pointers = parse_lotl(workspace)
        print(json.dumps({"count": len(pointers), "path": "notes/pointers.json"}, indent=2))
    else:
        metas = fetch_nationals(workspace, date=args.date, limit=args.limit)
        print(json.dumps({"count": len(metas), "date": args.date}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
