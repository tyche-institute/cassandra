#!/usr/bin/env python3
"""Validate Cassandra EATF missing-signing-input fixture.

This fixture verifies that absent signing material is explicit telemetry. It does
not validate trusted lists, signatures, legal status, supervision, compliance,
public alerts, or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "eatf_package_snapshot.py"
DATE = "synthetic-eatf-missing-signing"
FORBIDDEN_DIRECT_ASSERTIONS = [
    "legally valid",
    "signature is valid",
    "supervisory approval",
    "compliance passed",
    "public alert issued",
]


def write_json(path: pathlib.Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def seed_minimal_workspace(workspace: pathlib.Path) -> None:
    caveat = (
        "Synthetic Cassandra fixture for structural observation only; not "
        "trusted-list validation, signature validation, legal-status "
        "determination, supervision, compliance, public alerting, or "
        "publication approval."
    )
    write_json(workspace / "snapshots" / DATE / "manifest.json", {
        "date": DATE,
        "count": 1,
        "ok_count": 1,
        "error_count": 0,
        "items": [],
        "research_caveat": caveat,
    })
    write_json(workspace / "normalized" / DATE / "manifest.json", {
        "date": DATE,
        "count": 1,
        "ok_count": 1,
        "skipped_count": 0,
        "error_count": 0,
        "items": [],
        "research_caveat": caveat,
    })
    write_json(workspace / "diffs" / f"{DATE}.json", {
        "date": DATE,
        "baseline_created": False,
        "current_record_count": 0,
        "change_count": 0,
        "summary": {},
        "changes": [],
        "research_caveat": caveat,
    })


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cassandra-eatf-missing-") as tmp:
        workspace = pathlib.Path(tmp)
        seed_minimal_workspace(workspace)
        output_path = workspace / "notes" / "eatf-missing-signing-fixture-output.json"
        cmd = [
            sys.executable,
            str(SCRIPT),
            "--workspace",
            str(workspace),
            "--date",
            DATE,
            "--out-dir",
            "evidence",
            "--signing-profile",
            "fixture:no-signing-material",
            "--output",
            str(output_path.relative_to(workspace)),
        ]
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            raise AssertionError({"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})

        receipt_path = workspace / "evidence" / DATE / "eatf-verification.json"
        payload_path = workspace / "evidence" / DATE / "cassandra-observation.json"
        metadata_path = workspace / "evidence" / DATE / "eatf-metadata.json"
        for path in [receipt_path, payload_path, metadata_path, output_path]:
            if not path.exists():
                raise AssertionError(f"expected fixture artifact missing: {path}")

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        output = json.loads(output_path.read_text(encoding="utf-8"))
        assert receipt["status"] == "skipped_missing_signing_inputs"
        assert sorted(receipt["missing_inputs"]) == ["eatf_root", "private_key", "public_key", "timestamp"]
        assert receipt["aep_package"] is None
        assert receipt["payload"] == f"evidence/{DATE}/cassandra-observation.json"
        assert receipt["metadata"] == f"evidence/{DATE}/eatf-metadata.json"
        actual_payload_sha256 = hashlib.sha256(payload_path.read_bytes()).hexdigest()
        assert receipt["payload_sha256"] == actual_payload_sha256
        assert output["status"] == "skipped_missing_signing_inputs"
        assert output["receipt"]["status"] == "skipped_missing_signing_inputs"
        assert "trusted-list legal status" in payload["claim_boundary"]["does_not_assert"]

        serialized = json.dumps({"receipt": receipt, "payload": payload, "output": output}).lower()
        leaked = [phrase for phrase in FORBIDDEN_DIRECT_ASSERTIONS if phrase in serialized]
        if leaked:
            raise AssertionError(f"forbidden direct assertions in EATF fixture output: {leaked}")

    print(json.dumps({
        "status": "ok",
        "tested_case": "missing_signing_input_fixture",
        "expected_receipt_status": "skipped_missing_signing_inputs",
        "missing_inputs": ["eatf_root", "private_key", "public_key", "timestamp"],
        "caveat": "Synthetic EATF missing-input fixture only; explicit skip telemetry is not signature validation, legal-status evidence, supervision, compliance, public alerting, or publication approval.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
