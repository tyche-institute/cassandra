#!/usr/bin/env python3
"""Validate synthetic dashboard/public-index multi-state fixture.

This fixture checks dashboard-consumer behavior for ok, skipped, and failed EATF
states. It does not validate trusted lists, signatures, legal status,
supervision, compliance, public alerts, or publication readiness.
"""
from __future__ import annotations

import json
import pathlib

FIXTURE_PATH = pathlib.Path(__file__).parent / "fixtures" / "dashboard-public-index-multistate.json"
FORBIDDEN_DIRECT_ASSERTIONS = [
    "legally valid",
    "signature is valid",
    "supervisory approval",
    "compliance passed",
    "public alert issued",
]


def summarize_dashboard_states(index: dict) -> dict[str, object]:
    status_counts: dict[str, int] = {}
    dates_requiring_review: list[str] = []
    total_diff_changes = 0
    for run in index.get("runs", []):
        status = (run.get("eatf") or {}).get("status") or "missing"
        status_counts[status] = status_counts.get(status, 0) + 1
        total_diff_changes += int((run.get("counts") or {}).get("diff_change_count") or 0)
        if status != "ok" or int((run.get("counts") or {}).get("fetch_errors") or 0) > 0:
            dates_requiring_review.append(run.get("date"))
        caveat = run.get("caveat", "")
        if "not" not in caveat.lower():
            raise AssertionError(f"run caveat lacks explicit non-claim wording: {run.get('date')}")
    return {
        "status_counts": dict(sorted(status_counts.items())),
        "dates_requiring_review": dates_requiring_review,
        "total_diff_changes": total_diff_changes,
        "display_boundary": "Dashboard state is method telemetry only; it is not trusted-list validation, legal-status determination, signature validation, supervision, public alerting, or publication approval.",
    }


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture["case_study_sentence"] == "Cassandra: from governance infrastructure to evidence infrastructure."
    assert len(fixture["runs"]) == 3
    summary = summarize_dashboard_states(fixture)
    assert summary["status_counts"] == {"ok": 1, "skipped_missing_signing_inputs": 1, "verify_failed": 1}
    assert summary["dates_requiring_review"] == ["2099-01-02", "2099-01-03"]
    assert summary["total_diff_changes"] == 4

    serialized = json.dumps({"fixture": fixture, "summary": summary}).lower()
    leaked = [phrase for phrase in FORBIDDEN_DIRECT_ASSERTIONS if phrase in serialized]
    if leaked:
        raise AssertionError(f"forbidden direct assertions in dashboard fixture: {leaked}")

    print(json.dumps({
        "status": "ok",
        "fixture_path": str(FIXTURE_PATH),
        "tested_case": "dashboard_public_index_multistate",
        "summary": summary,
        "caveat": fixture["caveat"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
