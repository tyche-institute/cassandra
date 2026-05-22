#!/usr/bin/env python3
"""Append cautious no-fetch-before-gate paper prose.

Local research-only helper. It updates the Cassandra working draft with a short
aggregate-only subsection about the cadence gate that prevents fetch/overwrite
work before the next eligible UTC date. It does not assert legal compliance,
trusted-list legal effect, supervision, signature validation, public alerting,
regulated trust-service output, legal review, warning clearance, or publication
readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-no-fetch-gate-section-check-output.json"
ANCHOR = "## Operator review gates and non-publication status"
HEADING = "## No-fetch-before-gate maintenance discipline"

SECTION = """## No-fetch-before-gate maintenance discipline

Cassandra now has a local no-fetch-before-gate validator for periods when the cadence report says a real daily collection is not yet due. The validator reads `notes/daily-cadence-status-output.json`, runs guarded dry-run checks, and records whether the existing dated output roots would be mutated by the check. Its purpose is procedural: it helps a re-launched worker distinguish safe aggregate-only maintenance from a real fetch/normalize/diff/bundle/alert workflow. It is not evidence about public endpoint stability, trusted-list legal effect, signature validity, listed-entity status, or the presence or absence of any legally relevant event.

The paper interpretation rule is intentionally narrow. A status of `ok` in `notes/no-fetch-before-gate-validation-output.json` means that the local guard behaved as expected for the saved workspace state: same-date outputs remained protected, the next eligible date stayed dry-run-only, and snapshot output roots were not mutated during the check. It does not mean that external trusted-list endpoints were unchanged, reachable, complete, authoritative, or ready for comparison. If the validator reports an error, the safe response is workflow review, not endpoint interpretation and not public alerting.

This gate also protects append-only provenance. It avoids accidental same-date overwrites, preserves existing bundle and source evidence, and keeps future workers from treating maintenance refreshes as new longitudinal observations. Release notes, figures, and paper prose may cite the gate only as local workflow scheduling telemetry. Clean no-fetch validation does not assert legal effect, does not perform relying-party signature validation, does not supervise trusted lists, does not determine listed-entity status, does not provide public alerting, does not clear warnings, and does not approve publication.

"""

REFS_ANCHOR = "- `notes/daily-cadence-status-output.json`.\n"
REFS_EXTRA = "- `notes/no-fetch-before-gate-validation-output.json`.\n- `notes/paper-no-fetch-gate-section-check-output.json`.\n"

REQUIRED = [
    "no-fetch-before-gate validator",
    "safe aggregate-only maintenance",
    "not evidence about public endpoint stability",
    "does not assert legal effect",
    "does not perform relying-party signature validation",
    "does not supervise trusted lists",
    "does not determine listed-entity status",
    "does not provide public alerting",
    "does not clear warnings",
    "does not approve publication",
]

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
    "we provide eIDAS",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_section(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    start = text.index(heading)
    next_idx = text.find("\n## ", start + 1)
    return text[start:] if next_idx == -1 else text[start:next_idx]


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    errors: list[str] = []
    inserted = False
    refs_patched = False

    if HEADING not in text:
        if ANCHOR not in text:
            errors.append(f"missing anchor {ANCHOR!r}")
        else:
            text = text.replace(ANCHOR, SECTION + ANCHOR, 1)
            inserted = True

    if REFS_EXTRA not in text:
        if REFS_ANCHOR not in text:
            errors.append("missing references anchor for no-fetch gate section check")
        else:
            text = text.replace(REFS_ANCHOR, REFS_ANCHOR + REFS_EXTRA, 1)
            refs_patched = True

    if not errors:
        PAPER.write_text(text, encoding="utf-8")

    updated = PAPER.read_text(encoding="utf-8")
    section = extract_section(updated, HEADING)
    word_count = len([w for w in section.split() if w.strip()]) if section else 0
    if not section:
        errors.append("section heading missing after update")
    elif not 250 <= word_count <= 400:
        errors.append(f"section word count outside 250-400 target: {word_count}")
    missing = [fragment for fragment in REQUIRED if fragment not in section]
    if missing:
        errors.append(f"section missing required cautious fragments: {missing}")
    forbidden_hits = [token for token in FORBIDDEN if token.lower() in section.lower()]
    if forbidden_hits:
        errors.append(f"section contains forbidden tokens: {forbidden_hits}")

    result = {
        "schema": "urn:tyche:cassandra:paper-no-fetch-gate-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "heading": HEADING,
        "inserted": inserted,
        "refs_patched": refs_patched,
        "word_count": word_count,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, legal review, warning clearance, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
