#!/usr/bin/env python3
"""Append a cautious longitudinal aggregation and alert taxonomy section to paper/draft.md.

Research-only helper: this script does not publish or upload anything.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "paper" / "draft.md"
OUT = ROOT / "notes" / "paper-alert-taxonomy-section-check-output.json"
MARKER = "## Limitations and reproducibility"
SECTION_HEADING = "## Planned longitudinal aggregation and alert taxonomy"
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "we offer eIDAS-aligned trust services",
    "qualified trust service provider",
    "QTSP",
]

SECTION = """## Planned longitudinal aggregation and alert taxonomy

The longitudinal phase should treat each daily run as one row in an evidence trail and each machine-readable diff entry as a cautious observation nested inside that row. The first aggregation level is operational: pointer attempts, successful fetches, endpoint errors, XML-normalization successes, non-XML skips, parser errors, comparable records, and diff counts. These totals are useful for distinguishing corpus-collection conditions from structural XML changes. They should be reported as dated local telemetry, not as claims about the availability, validity, or legal status of any public list.

The second aggregation level is structural. Diff entries can be grouped by document addition or removal, normalized-hash change, scheme-summary field change, provider-inventory change, service-inventory change, and provider/service detail change. Counts should be summarized by date and territory code, with listed names kept out of prose. Hashed inventory keys can support continuity analysis across runs, but the draft should describe them as local comparison handles rather than identifiers with legal meaning.

The alert taxonomy should remain internal and descriptive. A baseline run can emit `baseline_initialized`; an empty comparison can emit `no_structural_diff_observed`; non-empty comparisons can emit `structural_diff_observed`; collection anomalies can emit `fetch_or_parse_telemetry_observed`. Severity labels, if added later, should reflect research triage effort rather than public risk or compliance effect. For example, a normalized-hash change may be high priority for manual inspection because it affects many records, while still carrying no statement about legal effect.

Paper figures can aggregate these classes as time series, stacked bars, or transition matrices once multiple dates exist. The caption language should state that the plots summarize local observations produced by a fixed method. Named case studies should remain deferred until the operator approves explicit examples and their wording.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    body = text.split("\n", 1)[1] if "\n" in text else text
    return len([token for token in body.replace("/", " ").split() if token.strip()])


def main() -> None:
    original = DRAFT.read_text(encoding="utf-8")
    if SECTION_HEADING in original:
        updated = original
        changed = False
    else:
        if MARKER not in original:
            raise SystemExit(f"marker not found: {MARKER}")
        updated = original.replace(MARKER, SECTION + "\n" + MARKER, 1)
        DRAFT.write_text(updated, encoding="utf-8")
        changed = True

    forbidden_hits = [phrase for phrase in FORBIDDEN if phrase in updated]
    result = {
        "status": "ok" if not forbidden_hits else "error",
        "changed": changed,
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "draft_path": str(DRAFT.relative_to(ROOT)),
        "draft_sha256": sha256(DRAFT),
        "section_heading": SECTION_HEADING,
        "section_word_count": word_count(SECTION),
        "forbidden_hits": forbidden_hits,
        "checks": {
            "has_tych_institute_affiliation": "Affiliation: Tyche Institute, Tallinn, Estonia" in updated,
            "mentions_zetes": "Zetes" in updated,
            "uses_aggregate_only_named_entity_policy": "listed names kept out of prose" in SECTION,
            "uses_internal_alert_taxonomy": "internal and descriptive" in SECTION,
        },
        "caveats": [
            "research-only structural observation",
            "no relying-party validation claim",
            "no legal-status determination",
            "no public alerting or supervision claim",
            "no listed-entity names in narrative prose without approval",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if (
        forbidden_hits
        or not result["checks"]["has_tych_institute_affiliation"]
        or result["checks"]["mentions_zetes"]
        or not result["checks"]["uses_internal_alert_taxonomy"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
