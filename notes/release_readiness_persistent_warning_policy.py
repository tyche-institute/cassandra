#!/usr/bin/env python3
"""Create a local note explaining persistent release-readiness warnings.

This helper is intentionally local and non-publishing. It summarizes why some
warnings are expected to persist across append-only Cassandra history without
clearing warnings, rewriting historical artifacts, or treating warning
classification as approval.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

NOTE_PATH = Path("notes/release-readiness-persistent-warning-policy.md")
REPORT_PATH = Path("notes/release-readiness-warning-report-output.json")

CAVEAT = (
    "This note is local workflow-maintenance context only. It does not clear "
    "warnings, rewrite historical artifacts, approve publication, perform legal "
    "review, validate signatures, supervise trusted lists, determine "
    "listed-entity status, provide public alerting, or create regulated "
    "trust-service output."
)


def load_report(workspace: Path) -> dict:
    return json.loads((workspace / REPORT_PATH).read_text(encoding="utf-8"))


def render_note(workspace: Path) -> str:
    report = load_report(workspace)
    classes = report.get("aggregate_warning_class_counts", {})
    created = datetime.now(timezone.utc).isoformat()
    warning_count = report.get("release_warning_count")
    class_lines = "\n".join(
        f"- `{name}`: {count} observed in the current warning report."
        for name, count in sorted(classes.items())
    )
    return f"""# Release-readiness persistent-warning policy note

Created: {created}
Source report: `{REPORT_PATH.as_posix()}`
Source report status: `{report.get('status')}`
Release-readiness warning sources: `{warning_count}`

## Purpose

This local note records which release-readiness warning classes are expected to persist across append-only Cassandra history. It exists to prevent future workers from treating stable, caveated warnings as either hard failures or as safe-to-clear items. It is not a publication gate and is not a legal review.

## Current persistent warning classes

{class_lines}

## Interpretation policy

Persistent warnings remain visible because Cassandra keeps append-only alert rows, historical bundle notes, generated SVG caveats, and repeated artifact-index rows as reproducibility evidence. The current warning-report output classifies these items as manual-review context only. A future worker may refresh validators and reports, but should not automatically delete historical rows, rewrite frozen bundles, or remove caveated words merely to obtain a zero-warning release-readiness checklist.

The expected maintenance posture is:

1. Keep hard errors at zero before any operator review.
2. Preserve warning classes that document legacy append-only context, caveated risky-phrase detections, or duplicate rows with at least one current matching hash.
3. Escalate to `BLOCKED.md` if a warning becomes an uncaveated claim of legal effect, supervision, relying-party signature validation, public alerting, regulated trust-service output, listed-entity status, or publication approval.
4. Treat any proposal to rewrite historical bundles, remove append-only alert entries, or publish externally as operator-review work, not autonomous worker cleanup.

## Non-clearance caveat

{CAVEAT}
"""


def main() -> int:
    workspace = Path.cwd()
    note_path = workspace / NOTE_PATH
    note = render_note(workspace)
    note_path.write_text(note, encoding="utf-8")
    result = {
        "status": "ok",
        "created": datetime.now(timezone.utc).isoformat(),
        "note": NOTE_PATH.as_posix(),
        "source_report": REPORT_PATH.as_posix(),
        "research_caveat": CAVEAT,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
