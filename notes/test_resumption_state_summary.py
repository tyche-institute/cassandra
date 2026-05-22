#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from summarize_resumption_state import build_summary, latest_progress_entry, write_markdown


class ResumptionStateSummaryTests(unittest.TestCase):
    def test_latest_progress_entry_extracts_next_action(self) -> None:
        text = """# Progress\n\n## 2026-05-21T00:00:00Z — older\n\nNext action: old.\n\n## 2026-05-22T00:00:00Z — gate-state exit\n\nBody.\n\nNext action: wait for 2026-05-23.\n"""
        entry = latest_progress_entry(text)
        self.assertTrue(entry["found"])
        self.assertEqual(entry["heading_timestamp"], "2026-05-22T00:00:00Z")
        self.assertEqual(entry["heading_title"], "gate-state exit")
        self.assertEqual(entry["next_action"], "Next action: wait for 2026-05-23.")

    def test_build_summary_is_aggregate_only_and_counts_local_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes").mkdir()
            (root / "snapshots" / "2026-05-22").mkdir(parents=True)
            (root / "normalized" / "2026-05-22").mkdir(parents=True)
            (root / "bundles" / "2026-05-22").mkdir(parents=True)
            (root / "diffs").mkdir()
            (root / "PLAN.md").write_text("plan\n", encoding="utf-8")
            (root / "HERMES_PROGRESS.md").write_text("## 2026-05-22T00:00:00Z — gate\n\nNext action: wait.\n", encoding="utf-8")
            (root / "ARTIFACT_INDEX.md").write_text("# Index\n", encoding="utf-8")
            (root / "SOURCES.md").write_text("# Sources\n", encoding="utf-8")
            (root / "CLAIMS.md").write_text("# Claims\n", encoding="utf-8")
            (root / "snapshots" / "2026-05-22" / "01-aa.xml").write_text("<x/>", encoding="utf-8")
            (root / "snapshots" / "2026-05-22" / "01-aa.xml.meta.json").write_text("{}", encoding="utf-8")
            (root / "normalized" / "2026-05-22" / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "bundles" / "2026-05-22" / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "diffs" / "2026-05-22.json").write_text("{}", encoding="utf-8")

            summary = build_summary(root)
            self.assertEqual(summary["schema"], "cassandra.resumption_state_summary.v1")
            self.assertEqual(summary["dated_lineages"]["latest_snapshot_date"], "2026-05-22")
            self.assertEqual(summary["dated_lineages"]["latest_date"], "2026-05-22")
            self.assertEqual(summary["latest_snapshot_date"], "2026-05-22")
            self.assertEqual(summary["latest_date"], "2026-05-22")
            self.assertEqual(summary["latest_completed_date"], "2026-05-22")
            self.assertEqual(summary["latest_dated_lineage"], "2026-05-22")
            self.assertEqual(summary["status"], "ok")
            self.assertEqual(summary["dated_lineages"]["latest_counts"]["snapshot_content_files"], 1)
            self.assertEqual(summary["latest_counts"]["snapshot_content_files"], 1)
            self.assertIn("Local workflow resumption telemetry only", summary["claim_boundary"])
            self.assertNotIn("legal effect evidence", summary["claim_boundary"])

            md = root / "notes" / "summary.md"
            write_markdown(summary, md)
            rendered = md.read_text(encoding="utf-8")
            self.assertIn("Latest snapshot date: 2026-05-22", rendered)
            self.assertIn("does not assert endpoint stability", rendered)


if __name__ == "__main__":
    unittest.main()
