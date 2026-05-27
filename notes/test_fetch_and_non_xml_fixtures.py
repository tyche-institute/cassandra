#!/usr/bin/env python3
"""Validate Cassandra synthetic fetch-failure and non-XML fixtures.

These fixtures exercise operational telemetry only. They do not validate trusted
lists, signatures, legal status, supervision, compliance, public alerts, or
publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import fetch  # noqa: E402
import parse  # noqa: E402

FORBIDDEN_DIRECT_ASSERTIONS = [
    "legally valid",
    "signature valid",
    "supervisory approval",
    "compliance passed",
    "public alert issued",
]


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        content: bytes,
        url: str,
        headers: dict[str, str] | None = None,
        history: list["FakeResponse"] | None = None,
    ) -> None:
        self.status_code = status_code
        self.content = content
        self.url = url
        self.headers = headers or {}
        self.history = history or []

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} synthetic response", response=self)


def run_fetch_fixture(workspace: pathlib.Path) -> dict[str, object]:
    original_get = fetch.requests.get
    calls: list[str] = []

    def fake_get(url: str, headers: dict[str, str], timeout: int) -> FakeResponse:
        calls.append(url)
        if url.endswith("timeout.xml"):
            raise requests.Timeout("synthetic timeout")
        if url.endswith("http-500.xml"):
            return FakeResponse(
                500,
                b"server error body",
                url,
                {"Content-Type": "application/xml", "Content-Length": "17"},
            )
        if url.endswith("redirect.xml"):
            history = [FakeResponse(302, b"", url, {"Location": "https://fixture.example/final.xml"})]
            return FakeResponse(
                200,
                b"<root/>",
                "https://fixture.example/final.xml",
                {"Content-Type": "application/xml", "Content-Length": "7"},
                history,
            )
        if url.endswith("unreachable.xml"):
            raise requests.ConnectionError("synthetic unreachable pointer")
        raise AssertionError(f"unexpected URL: {url}")

    fetch.requests.get = fake_get
    try:
        timeout_meta = fetch.fetch_url(
            "https://fixture.example/timeout.xml",
            workspace / "snapshots" / "synthetic-fetch" / "01-timeout.xml",
            timeout=1,
            allow_error=True,
        )
        http_meta = fetch.fetch_url(
            "https://fixture.example/http-500.xml",
            workspace / "snapshots" / "synthetic-fetch" / "02-http-500.xml",
            timeout=1,
            allow_error=True,
        )
        redirect_meta = fetch.fetch_url(
            "https://fixture.example/redirect.xml",
            workspace / "snapshots" / "synthetic-fetch" / "03-redirect.xml",
            timeout=1,
            allow_error=True,
        )
        unreachable_meta = fetch.fetch_url(
            "https://fixture.example/unreachable.xml",
            workspace / "snapshots" / "synthetic-fetch" / "04-unreachable.xml",
            timeout=1,
            allow_error=True,
        )
    finally:
        fetch.requests.get = original_get

    assert calls == [
        "https://fixture.example/timeout.xml",
        "https://fixture.example/http-500.xml",
        "https://fixture.example/redirect.xml",
        "https://fixture.example/unreachable.xml",
    ]
    assert timeout_meta["error"] == "Timeout"
    assert timeout_meta["http_status"] is None
    assert http_meta["error"] == "HTTPError"
    assert http_meta["http_status"] == 500
    assert http_meta["bytes"] == len(b"server error body")
    assert http_meta["sha256"] == hashlib.sha256(b"server error body").hexdigest()
    assert redirect_meta["http_status"] == 200
    assert redirect_meta["final_url"] == "https://fixture.example/final.xml"
    assert redirect_meta["redirect_count"] == 1
    assert redirect_meta["redirect_history"][0]["status_code"] == 302
    assert unreachable_meta["error"] == "ConnectionError"
    assert unreachable_meta["http_status"] is None

    return {
        "timeout": {"status": "ok", "error": timeout_meta["error"], "http_status": timeout_meta["http_status"]},
        "http_error": {"status": "ok", "error": http_meta["error"], "http_status": http_meta["http_status"], "bytes": http_meta["bytes"]},
        "redirect": {"status": "ok", "final_url": redirect_meta["final_url"], "redirect_count": redirect_meta["redirect_count"]},
        "unreachable_pointer": {"status": "ok", "error": unreachable_meta["error"], "http_status": unreachable_meta["http_status"]},
    }


def run_non_xml_fixture(workspace: pathlib.Path) -> dict[str, object]:
    date = "synthetic-non-xml"
    snapshot_dir = workspace / "snapshots" / date
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "01-valid.xml").write_text("<root><child>ok</child></root>", encoding="utf-8")
    (snapshot_dir / "02-document.pdf").write_bytes(b"%PDF-1.4 synthetic")
    (snapshot_dir / "03-page.html").write_text("<html><body>synthetic</body></html>", encoding="utf-8")
    (snapshot_dir / "04-text.txt").write_text("not xml", encoding="utf-8")
    (snapshot_dir / "05-broken.xml").write_text("<root>", encoding="utf-8")

    manifest = parse.normalize_snapshot(workspace, date)
    status_by_source = {pathlib.Path(item["source"]).name: item["status"] for item in manifest["items"]}
    assert manifest["count"] == 5
    assert manifest["ok_count"] == 1
    assert manifest["skipped_count"] == 3
    assert manifest["error_count"] == 1
    assert status_by_source["01-valid.xml"] == "ok"
    assert status_by_source["02-document.pdf"] == "skipped_non_xml"
    assert status_by_source["03-page.html"] == "skipped_non_xml"
    assert status_by_source["04-text.txt"] == "skipped_non_xml"
    assert status_by_source["05-broken.xml"] == "xml_parse_error"
    return {
        "manifest": "normalized/synthetic-non-xml/manifest.json",
        "status": "ok",
        "count": manifest["count"],
        "ok_count": manifest["ok_count"],
        "skipped_count": manifest["skipped_count"],
        "error_count": manifest["error_count"],
        "status_by_source": status_by_source,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cassandra-fixtures-") as tmp:
        workspace = pathlib.Path(tmp)
        tested_cases = {
            "fetch_failure_timeout_http_redirect_unreachable": run_fetch_fixture(workspace),
            "non_xml_and_non_parseable_input": run_non_xml_fixture(workspace),
        }
    serialized = json.dumps(tested_cases).lower()
    leaked = [phrase for phrase in FORBIDDEN_DIRECT_ASSERTIONS if phrase in serialized]
    if leaked:
        raise AssertionError(f"forbidden direct assertions in fixture output: {leaked}")
    print(json.dumps({
        "status": "ok",
        "tested_cases": tested_cases,
        "caveat": "Synthetic Cassandra fetch/non-XML fixtures for operational telemetry only; not legal-status, signature-validation, supervision, compliance, public-alerting, or publication evidence.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
