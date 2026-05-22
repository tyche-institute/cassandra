#!/usr/bin/env python3
"""Insert a release-readiness warning-report note into the Cassandra paper.

The note is deliberately abstention-oriented: it references the warning report
as manual-review context, not approval, publication readiness, legal evidence,
supervision, signature validation, public alerting, or regulated trust-service
output.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-release-warning-report-note-check-output.json"
MARKER = "The release-readiness warning report is a companion to that checklist, not a clearance mechanism."
INSERT_AFTER = (
    "For the current two-date corpus, the checklist remains local workflow telemetry over `notes/aggregate-results-2026-05-21-output.json`, "
    "`figures/aggregate-run-telemetry.svg`, `figures/aggregate-diff-classes.svg`, and the dated 2026-05-20/2026-05-21 snapshot, "
    "normalization, diff, alert, and bundle records. It should be refreshed after any new dated fetch or paper rewrite. Until the operator "
    "approves an external package, Cassandra outputs remain research-only working artifacts and should not be presented as public alerts, "
    "endpoint certification, supervisory findings, listed-entity status evidence, legal compliance evidence, regulated trust-service output, "
    "or publication approval."
)
PARAGRAPH = (
    "\n\n"
    "The release-readiness warning report is a companion to that checklist, not a clearance mechanism. "
    "`notes/release-readiness-warning-report-output.json` classifies preserved warnings from the release-readiness checklist so the operator can see whether they are caveated risky-phrase review items, legacy append-only alert context, or duplicate-row maintenance context. The report should be inspected together with the underlying validator outputs; it does not clear warnings, rewrite historical artifacts, approve external circulation, validate signatures for relying-party purposes, supervise any trusted list, assert listed-entity status, or turn local structural-observation telemetry into public alerting. If the warning classes change after a new dated run, the checklist should be treated as incomplete until the changed warning sources have been manually reviewed."
)
REQUIRED = [
    "release-readiness warning report",
    "notes/release-readiness-warning-report-output.json",
    "not a clearance mechanism",
    "does not clear warnings",
    "manual reviewed".replace("manual reviewed", "manually reviewed"),
    "public alerting",
]
FORBIDDEN_UNCAVEATED = ["publication ready", "ready for publication", "legal compliance evidence"]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    changed = False
    if MARKER not in text:
        if INSERT_AFTER not in text:
            raise SystemExit("anchor paragraph not found")
        text = text.replace(INSERT_AFTER, INSERT_AFTER + PARAGRAPH, 1)
        PAPER.write_text(text, encoding="utf-8")
        changed = True
    section_start = text.index("## Release-readiness checklist for operator review")
    section_end = text.find("\n## References and local evidence", section_start)
    section = text[section_start: section_end if section_end != -1 else len(text)]
    missing = [fragment for fragment in REQUIRED if fragment not in section]
    forbidden_hits = []
    lowered_section = section.lower()
    for phrase in FORBIDDEN_UNCAVEATED:
        start = 0
        while True:
            index = lowered_section.find(phrase, start)
            if index == -1:
                break
            local = lowered_section[max(0, index - 140): index + len(phrase) + 140]
            if not any(token in local for token in ["not ", "should not", "does not", "not a substitute", "not legal"]):
                forbidden_hits.append(phrase)
            start = index + len(phrase)
    result = {
        "schema": "urn:tyche:cassandra:paper-release-warning-report-note-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not missing and not forbidden_hits else "needs_review",
        "changed": changed,
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "missing_required_fragments": missing,
        "forbidden_hits": forbidden_hits,
        "research_caveat": "Release-readiness warning-report note check only; this does not clear warnings, approve publication, assert legal effect, validate signatures, supervise trusted lists, provide public alerting, or create regulated trust-service output.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
