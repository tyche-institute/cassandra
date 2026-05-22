#!/usr/bin/env python3
"""Validate that public paper prose stays aggregate-only for listed names.

This local validator derives a conservative set of raw listed-name candidates
from saved Cassandra snapshot XML files and checks that `paper/draft.md` does
not reproduce those candidates. Findings report hashes and line numbers only;
raw listed names are not echoed into validator output.

Research-only helper: it does not determine legal effect, trusted-list status,
signature validity, supervision, public alerting, or publication readiness.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterable

LISTED_NAME_ELEMENTS = {
    "TSPName",
    "TSPTradeName",
    "ServiceName",
}

MIN_CANDIDATE_LEN = 6

RESEARCH_CAVEAT = (
    "Local aggregate-only naming check for Cassandra paper prose; candidate "
    "names are derived from saved XML snapshots and findings are hash-only. "
    "This does not assert legal effect, trusted-list status, signature "
    "validity, supervision, public alerting, regulated trust-service output, "
    "legal review, or publication approval."
)


@dataclass
class Finding:
    path: str
    line: int
    candidate_sha256: str
    source_path: str
    element: str
    severity: str = "error"


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def hash_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def is_candidate(value: str) -> bool:
    value = normalize_text(value)
    if len(value) < MIN_CANDIDATE_LEN:
        return False
    if not any(ch.isalpha() for ch in value):
        return False
    lowered = value.lower()
    if lowered.startswith(("http://", "https://", "urn:")):
        return False
    # Avoid very broad language/status fragments that could be ordinary paper prose.
    generic = {
        "granted",
        "withdrawn",
        "deprecated",
        "recognised at national level",
        "supervision ceased",
    }
    return lowered not in generic


def latest_snapshot_dir(workspace: Path) -> Path | None:
    root = workspace / "snapshots"
    if not root.exists():
        return None
    dated = [p for p in root.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)]
    if not dated:
        return None
    return sorted(dated, key=lambda p: p.name)[-1]


def iter_snapshot_xml(snapshot_dir: Path) -> Iterable[Path]:
    for path in sorted(snapshot_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.endswith(".meta.json") or path.name == "manifest.json":
            continue
        if path.suffix.lower() in {".xml", ".xtsl"}:
            yield path


def extract_candidate_keys(workspace: Path) -> tuple[list[tuple[str, dict]], list[dict], str | None]:
    snapshot_dir = latest_snapshot_dir(workspace)
    if snapshot_dir is None:
        return [], [{"path": "snapshots/", "error": "no dated snapshot directories found"}], None

    candidates: dict[str, dict] = {}
    parse_errors: list[dict] = []
    for path in iter_snapshot_xml(snapshot_dir):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            parse_errors.append({"path": str(path.relative_to(workspace)), "error": type(exc).__name__})
            continue
        for element in root.iter():
            element_name = local_name(element.tag)
            if element_name not in LISTED_NAME_ELEMENTS:
                continue
            value = normalize_text(" ".join(element.itertext()))
            if not is_candidate(value):
                continue
            key = value.casefold()
            candidates.setdefault(
                key,
                {
                    "candidate_sha256": hash_text(key),
                    "source_path": str(path.relative_to(workspace)),
                    "element": element_name,
                    "length": len(value),
                },
            )
    return sorted(candidates.items(), key=lambda item: item[1]["candidate_sha256"]), parse_errors, snapshot_dir.name


def scan_paper_with_keys(workspace: Path, candidate_items: list[tuple[str, dict]]) -> tuple[list[Finding], dict | None]:
    paper_path = workspace / "paper" / "draft.md"
    if not paper_path.exists():
        return [], None
    text = paper_path.read_text(encoding="utf-8")
    lowered = text.casefold()
    findings: list[Finding] = []
    for key, metadata in candidate_items:
        index = lowered.find(key)
        if index < 0:
            continue
        findings.append(
            Finding(
                path=str(paper_path.relative_to(workspace)),
                line=line_number(text, index),
                candidate_sha256=metadata["candidate_sha256"],
                source_path=metadata["source_path"],
                element=metadata["element"],
            )
        )
    return findings, {
        "path": str(paper_path.relative_to(workspace)),
        "sha256": sha256(paper_path.read_bytes()).hexdigest(),
        "bytes": paper_path.stat().st_size,
        "line_count": text.count("\n") + (1 if text else 0),
    }


def validate(workspace: Path) -> dict:
    candidate_items, parse_errors, snapshot_date = extract_candidate_keys(workspace)
    public_candidate_metadata = [metadata for _key, metadata in candidate_items]
    findings, paper_stats = scan_paper_with_keys(workspace, candidate_items)
    missing_files = [] if paper_stats is not None else ["paper/draft.md"]
    status = "ok"
    if missing_files or findings:
        status = "needs_review"
    return {
        "schema": "urn:tyche:cassandra:paper-aggregate-only-naming:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": status,
        "snapshot_date_scanned": snapshot_date,
        "candidate_count": len(public_candidate_metadata),
        "candidate_elements": sorted(LISTED_NAME_ELEMENTS),
        "candidate_inventory_hash": hash_text(json.dumps(public_candidate_metadata, sort_keys=True)),
        "missing_files": missing_files,
        "parse_error_count": len(parse_errors),
        "parse_errors": parse_errors,
        "paper_stats": paper_stats,
        "findings": [asdict(finding) for finding in findings],
        "error_count": len(findings) + len(missing_files),
        "warning_count": len(parse_errors),
        "raw_names_echoed": False,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output", default="notes/paper-aggregate-only-naming-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output_path = workspace / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
