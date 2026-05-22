#!/usr/bin/env python3
"""Append a source/bundle row coverage interpretation section to paper/draft.md.

This helper is intentionally idempotent. It documents how SOURCES.md date-specific
bundle rows should be interpreted as local provenance links, not as endpoint,
legal-status, signature-validation, supervision, public-alerting, warning-clearance,
legal-review, or publication evidence. It does not fetch endpoints or mutate dated
snapshot, normalization, diff, alert, or bundle outputs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "draft.md"
OUTPUT = ROOT / "notes" / "paper-source-bundle-row-coverage-section-check-output.json"
HEADING = "## Source-bundle row coverage interpretation"
SECTION = """
## Source-bundle row coverage interpretation

`SOURCES.md` now includes date-specific rows that link each completed local Cassandra lineage to its corresponding evidence-bundle manifest. Those rows are provenance pointers, not new observations of live trusted-list endpoints. They help a reviewer move from an aggregate statement in the paper to the local bundle for a saved run, including manifest, claims, notes, verification metadata, and source references. The local coverage output, `notes/sources-bundle-row-coverage-output.json`, checks that completed dated lineages have source-register rows and bundle manifests, but it does not fetch endpoints or reinterpret the saved XML, PDF, diff, alert, or bundle contents.

The safe interpretation is narrow: date-specific source rows improve traceability between the source register and locally stored evidence bundles. They do not mean that an endpoint was stable, that a trusted-list document had legal effect, that a signature was validated for relying-party purposes, that a supervisory conclusion was reached, or that a listed entity had any status. A missing row should be treated as local provenance-maintenance debt; a clean coverage result should be treated as local register completeness for the configured lineages.

For publication-facing prose, bundle-row coverage should support citations and reproducibility statements rather than substantive status claims. A sentence may say that the study's local register links completed dated lineages to bundle manifests, with caveats preserved in the bundle notes. It should not say that bundle rows certify the run, clear warnings, approve release, or convert structural diffs into public alerts. Any decision to circulate a bundle, dataset slice, or named example remains outside this autonomous workflow and requires operator review.
""".strip() + "\n"

REFERENCES = [
    "notes/sources-bundle-row-coverage-output.json",
]


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    changed = False
    if HEADING not in text:
        marker = "## References and local evidence"
        if marker not in text:
            raise SystemExit(f"missing insertion marker: {marker}")
        text = text.replace(marker, SECTION + "\n" + marker, 1)
        changed = True
    for ref in REFERENCES:
        bullet = f"- `{ref}`."
        if bullet not in text:
            text = text.rstrip() + "\n" + bullet + "\n"
            changed = True
    if changed:
        PAPER.write_text(text, encoding="utf-8")
    out = {
        "status": "ok",
        "changed": changed,
        "heading": HEADING,
        "word_count": len(SECTION.split()),
        "references": REFERENCES,
        "caveats": [
            "local source-register provenance only",
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
