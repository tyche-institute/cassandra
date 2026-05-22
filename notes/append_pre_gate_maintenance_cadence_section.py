#!/usr/bin/env python3
"""Append the pre-gate maintenance cadence section to paper/draft.md.

This helper is intentionally idempotent: it only inserts the section when the
heading is absent. It does not fetch endpoints, inspect live trusted-list data,
or alter dated snapshot, normalization, diff, alert, or bundle outputs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "draft.md"
OUTPUT = ROOT / "notes" / "paper-pre-gate-maintenance-cadence-section-check-output.json"
HEADING = "## Pre-gate maintenance cadence limits"
SECTION = """
## Pre-gate maintenance cadence limits

When the cadence report says that a real daily collection is not yet due, Cassandra should prefer one bounded aggregate-only maintenance action over repeated validator refreshes. A useful pre-gate action may update paper wording, document a local workflow boundary, or refresh a validator that is stale because a dependent file changed. It should not fetch public endpoints, overwrite dated snapshot roots, rename historical lineages, or convert waiting-period telemetry into claims about the external trusted-list ecosystem.

This limit is a provenance rule as much as a time-management rule. Repeatedly rewriting the same validation outputs can create hash churn in `ARTIFACT_INDEX.md` without adding a new longitudinal observation. The correct interpretation is therefore narrow: a clean no-fetch or paper-boundary validator confirms that the current local workspace still respects configured guardrails, not that a public endpoint is stable, that a legally relevant event did or did not occur, or that the paper is ready for release. If no concrete aggregate-only improvement is available, the safer autonomous action is to record the gate state and exit rather than manufacture additional evidence.

Once the next eligible UTC date arrives, this maintenance posture should yield to the guarded daily workflow. The worker should create a new dated snapshot lineage, normalize comparable XML, compute the configured diff, update the evidence bundle and alert roll-up, and then refresh aggregate tables, figures, and paper validators. Until that point, pre-gate work remains local workflow hygiene only. It does not perform relying-party signature validation, supervise trusted lists, determine listed-entity status, provide public alerting, clear legal review, or approve publication.
""".strip()+"\n"


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    changed = False
    if HEADING not in text:
        marker = "## References and local evidence"
        if marker not in text:
            raise SystemExit(f"missing insertion marker: {marker}")
        text = text.replace(marker, SECTION + "\n" + marker, 1)
        PAPER.write_text(text, encoding="utf-8")
        changed = True
    out = {
        "status": "ok",
        "changed": changed,
        "heading": HEADING,
        "word_count": len(SECTION.split()),
        "caveats": [
            "local workflow hygiene only",
            "not endpoint/status evidence",
            "not legal effect",
            "not signature validation",
            "not supervision",
            "not listed-entity status evidence",
            "not public alerting",
            "not legal review",
            "not publication approval",
        ],
        "raw_listed_names_intended": False,
    }
    OUTPUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
