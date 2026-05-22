#!/usr/bin/env python3
"""Smoke tests for validate_paper_aggregate_only_naming.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("validate_paper_aggregate_only_naming.py")
spec = importlib.util.spec_from_file_location("validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["validator"] = validator
spec.loader.exec_module(validator)

SNAPSHOT_XML = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<TrustServiceStatusList xmlns=\"http://uri.etsi.org/02231/v2#\">
  <TrustServiceProvider>
    <TSPInformation>
      <TSPName><Name xml:lang=\"en\">Example Trusted Provider Ltd</Name></TSPName>
      <TSPTradeName><Name xml:lang=\"en\">Example TSP Brand</Name></TSPTradeName>
    </TSPInformation>
    <TSPServices>
      <TSPService>
        <ServiceInformation>
          <ServiceName><Name xml:lang=\"en\">Example Certificate Service</Name></ServiceName>
        </ServiceInformation>
      </TSPService>
    </TSPServices>
  </TrustServiceProvider>
</TrustServiceStatusList>
"""


def make_workspace(paper_text: str) -> Path:
    root = Path(tempfile.mkdtemp(prefix="cassandra-aggregate-only-naming-"))
    (root / "paper").mkdir(parents=True)
    (root / "snapshots" / "2026-05-22").mkdir(parents=True)
    (root / "paper" / "draft.md").write_text(paper_text, encoding="utf-8")
    (root / "snapshots" / "2026-05-22" / "01-aa.xml").write_text(SNAPSHOT_XML, encoding="utf-8")
    return root


def assert_no_raw_name_echo(result: dict) -> None:
    serialized = json.dumps(result, sort_keys=True)
    assert "Example Trusted Provider Ltd" not in serialized
    assert "Example TSP Brand" not in serialized
    assert "Example Certificate Service" not in serialized
    assert result["raw_names_echoed"] is False


def test_aggregate_only_paper_ok() -> None:
    root = make_workspace(
        "# Draft\n\nThis paper reports aggregate structural-observation telemetry only. "
        "It omits raw listed names and does not assert legal effect.\n"
    )
    result = validator.validate(root)
    assert result["status"] == "ok"
    assert result["candidate_count"] == 3
    assert result["error_count"] == 0
    assert_no_raw_name_echo(result)


def test_raw_provider_name_is_hash_only_error() -> None:
    root = make_workspace(
        "# Draft\n\nThis unsafe example names Example Trusted Provider Ltd in public prose.\n"
    )
    result = validator.validate(root)
    assert result["status"] == "needs_review"
    assert result["error_count"] == 1
    assert result["findings"][0]["line"] == 3
    assert result["findings"][0]["element"] == "TSPName"
    assert_no_raw_name_echo(result)


def test_latest_snapshot_directory_is_used() -> None:
    root = make_workspace("# Draft\n\nOld Provider Name is not checked when only present in older snapshots.\n")
    old_dir = root / "snapshots" / "2026-05-21"
    old_dir.mkdir(parents=True)
    (old_dir / "01-aa.xml").write_text(
        SNAPSHOT_XML.replace("Example Trusted Provider Ltd", "Old Provider Name"),
        encoding="utf-8",
    )
    result = validator.validate(root)
    assert result["snapshot_date_scanned"] == "2026-05-22"
    assert result["status"] == "ok"
    assert_no_raw_name_echo(result)


def main() -> int:
    tests = [
        test_aggregate_only_paper_ok,
        test_raw_provider_name_is_hash_only_error,
        test_latest_snapshot_directory_is_used,
    ]
    results = []
    for test in tests:
        test()
        results.append({"test": test.__name__, "status": "ok"})
    print(json.dumps({"status": "ok", "tests": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
