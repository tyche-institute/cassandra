#!/usr/bin/env python3
"""Validate synthetic Cassandra EATF success and tamper fixtures.

This fixture uses a temporary fake EATF CLI and synthetic non-secret keys. It
checks Cassandra's package/receipt handling only. It does not validate trusted
lists, source signatures, legal status, supervision, compliance, public alerts,
or publication readiness.
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
DATE = "synthetic-eatf-success-tamper"
CAVEAT = (
    "Synthetic EATF success/tamper fixture for Cassandra package handling only; "
    "not trusted-list validation, signature validation, legal-status "
    "determination, supervision, compliance, public alerting, or publication "
    "approval."
)
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


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_minimal_workspace(workspace: pathlib.Path) -> None:
    write_json(workspace / "snapshots" / DATE / "manifest.json", {
        "date": DATE,
        "count": 1,
        "ok_count": 1,
        "error_count": 0,
        "items": [],
        "research_caveat": CAVEAT,
    })
    write_json(workspace / "normalized" / DATE / "manifest.json", {
        "date": DATE,
        "count": 1,
        "ok_count": 1,
        "skipped_count": 0,
        "error_count": 0,
        "items": [],
        "research_caveat": CAVEAT,
    })
    write_json(workspace / "diffs" / f"{DATE}.json", {
        "date": DATE,
        "baseline_created": False,
        "current_record_count": 1,
        "change_count": 0,
        "summary": {},
        "changes": [],
        "research_caveat": CAVEAT,
    })


def write_fake_eatf_cli(workspace: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    eatf_root = workspace / "fake-eatf"
    sign_cli = eatf_root / "cli" / "eatf-sign" / "bin" / "eatf-sign.js"
    verify_cli = eatf_root / "cli" / "eatf-verify" / "bin" / "eatf-verify.js"
    sign_cli.parent.mkdir(parents=True, exist_ok=True)
    verify_cli.parent.mkdir(parents=True, exist_ok=True)
    sign_cli.write_text(
        """#!/usr/bin/env node
const fs = require('fs');
const crypto = require('crypto');
function arg(name) { const i = process.argv.indexOf(name); return i >= 0 ? process.argv[i + 1] : null; }
const payload = arg('--payload');
const metadata = arg('--metadata');
const out = arg('--out');
const scope = arg('--scope');
const timestamp = arg('--timestamp');
const packageObj = {
  schema: 'urn:tyche:cassandra:fixture-aep:0.1',
  fixture: true,
  signature: 'fixture-ok',
  scope,
  timestamp,
  payload_path: payload,
  payload_sha256: crypto.createHash('sha256').update(fs.readFileSync(payload)).digest('hex'),
  metadata_path: metadata,
  metadata_sha256: crypto.createHash('sha256').update(fs.readFileSync(metadata)).digest('hex'),
  caveat: 'Fixture package verifies package bytes only; not trusted-list validation, signature validation, legal-status determination, supervision, public alerting, or publication approval.'
};
fs.mkdirSync(require('path').dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(packageObj, null, 2) + String.fromCharCode(10));
console.log(JSON.stringify({ signed: true, out }));
""",
        encoding="utf-8",
    )
    verify_cli.write_text(
        """#!/usr/bin/env node
const fs = require('fs');
const crypto = require('crypto');
const aep = process.argv[2];
let obj;
try { obj = JSON.parse(fs.readFileSync(aep, 'utf8')); } catch (err) {
  console.log(JSON.stringify({ valid: false, error: 'unparseable_fixture_aep' }));
  process.exit(1);
}
let valid = obj.signature === 'fixture-ok';
if (valid && obj.payload_path && fs.existsSync(obj.payload_path)) {
  const actual = crypto.createHash('sha256').update(fs.readFileSync(obj.payload_path)).digest('hex');
  valid = actual === obj.payload_sha256;
}
const result = {
  valid,
  fixture: true,
  status: valid ? 'ok' : 'verify_failed',
  caveat: 'Fixture verification checks synthetic package bytes only; not trusted-list validation, source signature validity, legal status, supervision, public alerting, or publication approval.'
};
console.log(JSON.stringify(result));
process.exit(valid ? 0 : 1);
""",
        encoding="utf-8",
    )
    sign_cli.chmod(0o755)
    verify_cli.chmod(0o755)
    key_path = workspace / "fixture-private-key.pem"
    public_key_path = workspace / "fixture-public-key.pem"
    key_path.write_text("fixture-private-key-not-secret\n", encoding="utf-8")
    public_key_path.write_text("fixture-public-key-not-secret\n", encoding="utf-8")
    return eatf_root, key_path, public_key_path


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cassandra-eatf-success-tamper-") as tmp:
        workspace = pathlib.Path(tmp)
        seed_minimal_workspace(workspace)
        eatf_root, key_path, public_key_path = write_fake_eatf_cli(workspace)
        output_path = workspace / "notes" / "eatf-success-tamper-fixture-output.json"
        cmd = [
            sys.executable,
            str(SCRIPT),
            "--workspace",
            str(workspace),
            "--date",
            DATE,
            "--out-dir",
            "evidence",
            "--eatf-root",
            str(eatf_root),
            "--key",
            str(key_path),
            "--public-key",
            str(public_key_path),
            "--timestamp",
            "fixture-timestamp-token",
            "--timestamp-label",
            "fixture:synthetic-timestamp",
            "--signing-profile",
            "fixture:synthetic-non-secret-key",
            "--output",
            str(output_path.relative_to(workspace)),
        ]
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            raise AssertionError({"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})

        receipt_path = workspace / "evidence" / DATE / "eatf-verification.json"
        payload_path = workspace / "evidence" / DATE / "cassandra-observation.json"
        aep_path = workspace / "evidence" / DATE / "cassandra-observation.aep"
        output = json.loads(output_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        package = json.loads(aep_path.read_text(encoding="utf-8"))
        assert receipt["status"] == "ok"
        assert receipt["verify"]["valid"] is True
        assert receipt["aep_sha256"] == sha256_file(aep_path)
        assert receipt["payload_sha256"] == sha256_file(payload_path)
        assert receipt["signing_profile"] == "fixture:synthetic-non-secret-key"
        assert output["status"] == "ok"
        assert package["signature"] == "fixture-ok"

        package["signature"] = "tampered-fixture-signature"
        package["tamper_note"] = "synthetic payload altered after package creation"
        aep_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verify_cli = eatf_root / "cli" / "eatf-verify" / "bin" / "eatf-verify.js"
        tamper_proc = subprocess.run(["node", str(verify_cli), str(aep_path), "--json"], text=True, capture_output=True, check=False)
        if tamper_proc.returncode == 0:
            raise AssertionError({"returncode": tamper_proc.returncode, "stdout": tamper_proc.stdout, "stderr": tamper_proc.stderr})
        tamper_result = json.loads(tamper_proc.stdout.strip().splitlines()[-1])
        assert tamper_result["valid"] is False
        assert tamper_result["status"] == "verify_failed"

        serialized = json.dumps({"receipt": receipt, "output": output, "tamper_result": tamper_result}).lower()
        leaked = [phrase for phrase in FORBIDDEN_DIRECT_ASSERTIONS if phrase in serialized]
        if leaked:
            raise AssertionError(f"forbidden direct assertions in EATF success/tamper fixture output: {leaked}")

    print(json.dumps({
        "status": "ok",
        "tested_cases": ["eatf_success_fixture", "eatf_tamper_fixture"],
        "success_receipt_status": "ok",
        "tamper_expected_status": "verify_failed",
        "signing_profile": "fixture:synthetic-non-secret-key",
        "caveat": CAVEAT,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
