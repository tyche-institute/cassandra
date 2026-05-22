#!/usr/bin/env python3
"""Append a bounded state-register reading section to paper/draft.md.

This helper is intentionally idempotent. It documents how workers should read
large append-only Cassandra registers without treating pagination or helper
summaries as endpoint/status evidence. It does not fetch endpoints, inspect live
trusted-list data, or alter dated snapshot, normalization, diff, alert, or bundle
outputs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "draft.md"
OUTPUT = ROOT / "notes" / "paper-bounded-state-register-reading-section-check-output.json"
HEADING = "## Bounded state-register reading discipline"
SECTION = """
## Bounded state-register reading discipline

Cassandra keeps several registers as append-only evidence ledgers, so mature runs can make `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, and `CLAIMS.md` too large for a single safe read. Bounded reading is therefore a workflow requirement rather than a shortcut. A worker should first run the exact state-file existence guard, then read `PLAN.md` in full, read recent windows from oversized registers, and use compact local summaries only as navigation aids. If a helper output reports counts or next-action text, those fields should be interpreted through the helper's declared schema keys and cross-checked against the underlying dated lineage files when a real collection or publication-facing change depends on them.

This reading discipline also limits claim formation. A failed full-file read, a truncated tool response, or a compact summary must not be converted into an assertion that endpoint behavior is stable, that a structural diff is absent, or that any listed entity has a particular status. The safe claim is narrower: the local workspace has append-only registers whose current size requires pagination or schema-aware summary reading for autonomous resumption. That is reproducibility and scheduling telemetry only, not trusted-list validation, legal-status evidence, relying-party signature validation, supervision, public alerting, warning clearance, legal review, or publication approval.

For maintenance periods before the next UTC collection gate, bounded reading should reduce churn. The worker should avoid revalidating the same outputs solely because a previous full-register read exceeded tool limits. When a concrete aggregate-only improvement is made, validators may be refreshed because dependent files changed; otherwise, the correct action is to record the gate state and exit. The underlying dated snapshots, normalized files, diffs, bundles, alerts, and source copies remain the evidence base for future longitudinal work.
""".strip() + "\n"


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
            "workflow reading discipline only",
            "not endpoint/status evidence",
            "not legal effect",
            "not signature validation",
            "not supervision",
            "not listed-entity status evidence",
            "not public alerting",
            "not warning clearance",
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
