#!/usr/bin/env python3
"""Add two-date aggregate-validation gate prose to Cassandra paper.

Local research-only helper. It updates the working draft with cautious prose and
performs minimal local checks. It does not assert legal compliance, trusted-list
legal effect, supervision, signature validation, public alerting, regulated
trust-service output, or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-two-date-gate-section-check-output.json"
ANCHOR = "## Results presentation and figure design"
HEADING = "## Two-date aggregate-validation gate"

SECTION = """## Two-date aggregate-validation gate

The second completed local lineage changes Cassandra from a bootstrap-only draft into a minimal multi-day workflow test, but it still does not support trend or status conclusions. The current aggregate-results output records two dated rows, `2026-05-20` and `2026-05-21`, derived from saved manifests, dated diffs, bundle records, and alert telemetry. Across those two rows the workflow attempted 86 LOTL-derived pointers, recorded 83 fetched content files and 3 fetch errors, normalized 62 XML artifacts, recorded 2 XML parser errors, and emitted zero aggregate structural diff entries under the configured parser and baseline. These totals are useful for checking lineage and figure generation; they are not evidence that the trusted-list ecosystem was stable, legally unchanged, or suitable for reliance.

The gate should therefore be read procedurally. A two-date table is enough to verify that collection, normalization, comparison, bundle creation, alert roll-up, aggregation, figure rendering, and multi-day validation can consume more than one dated state without rewriting earlier evidence. It is not enough to characterize churn rate, country behavior, authority performance, provider status, service quality, or supervisory significance. The safe result sentence is narrow: the local two-date validation completed against saved Cassandra artifacts and found no configured structural diff entries in the aggregate-results file.

Future rows should preserve the same interpretation discipline. If a later date emits nonzero diff entries, the paper should first check lineage parity and aggregate class counts, then describe the outcome as structural diff observed in local saved artifacts. If a later date again emits zero entries, the paper should keep the wording at the parser/baseline level. Named examples, release packaging, and any external circulation remain operator-review decisions; clean validation output is not publication approval, legal review, signature validation, supervision, public alerting, listed-entity status evidence, or regulated trust-service output.

"""

AGG_OLD = """The current aggregate-results table is deliberately small: it contains one dated row for the first local run. That limitation is useful because it fixes the semantics of the table before a longer series creates pressure for interpretation. The row for 2026-05-20 records 43 LOTL-derived pointer attempts, 41 fetched content files, 2 fetch errors, 31 normalized XML artifacts, 9 non-XML skips, 1 XML parsing error, and 31 comparable records in the baseline comparison. It also records zero diff entries because the comparison initialized the baseline rather than comparing against an earlier day. These values should be read as workflow telemetry with local evidence pointers, not as statements about the public legal status of any list, provider, service, or authority."""
AGG_NEW = """The current aggregate-results table is deliberately small: it contains two dated rows for the first completed local lineages. That limitation is useful because it fixes the semantics of the table before a longer series creates pressure for interpretation. The rows for 2026-05-20 and 2026-05-21 together record 86 LOTL-derived pointer attempts, 83 fetched content files, 3 fetch errors, 62 normalized XML artifacts, 19 non-XML skips, 2 XML parsing errors, and 62 comparable records across the two local comparisons. They also record zero aggregate diff entries under the configured parser and baseline. These values should be read as workflow telemetry with local evidence pointers, not as statements about the public legal status of any list, provider, service, or authority."""

FIG_OLD = """The first rendered figures are intentionally modest because the available series currently contains one dated run. `figures/aggregate-run-telemetry.svg` visualizes collection and normalization counts from the aggregate-results table, while `figures/aggregate-diff-classes.svg` visualizes the same row's diff-class totals. Both figures are derived from `notes/aggregate-results-table.csv` and `notes/aggregate-results-2026-05-20-output.json`, so the draft should treat them as reproducible views of local telemetry rather than as independent evidence. A future revision with multiple dates can reuse the same paths and checks, but the caption discipline should remain unchanged."""
FIG_NEW = """The rendered figures remain intentionally modest because the available series currently contains two dated local runs. `figures/aggregate-run-telemetry.svg` visualizes collection and normalization counts from the aggregate-results table, while `figures/aggregate-diff-classes.svg` visualizes the same table's diff-class totals. The first one-date renderer output remains recorded as `notes/aggregate-results-2026-05-20-output.json`; the current refreshed figures are derived from `notes/aggregate-results-table.csv` and `notes/aggregate-results-2026-05-21-output.json`. The draft should treat both figures as reproducible views of local telemetry rather than as independent evidence, and the caption discipline should remain unchanged as more dates are added."""

REFS_ANCHOR = "- `bundles/2026-05-20/snapshot-summary.json.bundle/`.\n"
REFS_EXTRA = """- `snapshots/2026-05-21/manifest.json`.
- `normalized/2026-05-21/manifest.json`.
- `diffs/2026-05-21.json`.
- `bundles/2026-05-21/snapshot-summary.json.bundle/`.
- `notes/aggregate-results-2026-05-21-output.json`.
- `notes/multiday-readiness-validation-output.json`.
"""

REQUIRED = [
    "two dated rows",
    "86 LOTL-derived pointers",
    "zero aggregate structural diff entries",
    "not evidence that the trusted-list ecosystem was stable",
    "not enough to characterize churn rate",
    "operator-review decisions",
    "not publication approval",
    "signature validation",
    "public alerting",
]
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees compliance",
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
    patched_aggregate = False
    patched_figure = False
    patched_refs = False

    if AGG_OLD in text:
        text = text.replace(AGG_OLD, AGG_NEW, 1)
        patched_aggregate = True
    elif AGG_NEW not in text:
        errors.append("aggregate telemetry paragraph not found for patching")

    if FIG_OLD in text:
        text = text.replace(FIG_OLD, FIG_NEW, 1)
        patched_figure = True
    elif FIG_NEW not in text:
        errors.append("figure reproducibility paragraph not found for patching")

    if HEADING not in text:
        if ANCHOR not in text:
            errors.append(f"missing anchor {ANCHOR!r}")
        else:
            text = text.replace(ANCHOR, SECTION + ANCHOR, 1)
            inserted = True

    if REFS_EXTRA not in text:
        if REFS_ANCHOR in text:
            text = text.replace(REFS_ANCHOR, REFS_ANCHOR + REFS_EXTRA, 1)
            patched_refs = True
        else:
            errors.append("references anchor not found for 2026-05-21 evidence refs")

    if not errors:
        PAPER.write_text(text, encoding="utf-8")

    updated = PAPER.read_text(encoding="utf-8")
    section = extract_section(updated, HEADING)
    word_count = len([w for w in section.split() if w.strip()]) if section else 0
    if not section:
        errors.append("section heading missing after update")
    elif not 250 <= word_count <= 400:
        errors.append(f"section word count outside 250-400 target: {word_count}")
    missing = [frag for frag in REQUIRED if frag not in section]
    if missing:
        errors.append(f"section missing required cautious fragments: {missing}")
    forbidden_hits = [token for token in FORBIDDEN if token.lower() in section.lower()]
    if forbidden_hits:
        errors.append(f"section contains forbidden tokens: {forbidden_hits}")

    result = {
        "schema": "urn:tyche:cassandra:paper-two-date-gate-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "heading": HEADING,
        "inserted": inserted,
        "patched_aggregate_paragraph": patched_aggregate,
        "patched_figure_paragraph": patched_figure,
        "patched_references": patched_refs,
        "word_count": word_count,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
