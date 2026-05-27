#!/usr/bin/env python3
"""Tests for the public Cassandra observatory index schema."""

from __future__ import annotations

import json
import pathlib
import unittest


WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = WORKSPACE / "observatory" / "public" / "data" / "schema.json"
INDEX_PATH = WORKSPACE / "observatory" / "public" / "data" / "index.json"


class PublicIndexSchemaTest(unittest.TestCase):
    def load_json(self, path: pathlib.Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_schema_file_exists_and_declares_public_index_id(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        self.assertEqual(schema["$id"], "urn:tyche:cassandra:observatory-public-index:0.1")
        self.assertIn("Public Cassandra observatory index", schema["title"])
        self.assertIn("claim_boundary", schema["required"])
        self.assertIn("runs", schema["required"])

    def test_current_public_index_conforms_to_schema_contract(self) -> None:
        schema = self.load_json(SCHEMA_PATH)
        index = self.load_json(INDEX_PATH)
        self.assertEqual(index["schema"], schema["$id"])
        for field in schema["required"]:
            self.assertIn(field, index)
        self.assertEqual(index["project"], "cassandra")
        self.assertEqual(index["case_study_sentence"], "Cassandra: from governance infrastructure to evidence infrastructure.")
        self.assertEqual(index["run_count"], len(index["runs"]))
        self.assertGreaterEqual(index["eatf_verified_count"], 0)
        self.assertLessEqual(index["eatf_verified_count"], index["run_count"])
        self.assertIn("legal effect of any trusted list", index["claim_boundary"]["does_not_assert"])
        self.assertIn("signature or certificate validity", index["claim_boundary"]["does_not_assert"])
        self.assertIn("absence of legally relevant change", index["claim_boundary"]["does_not_assert"])

    def test_each_run_preserves_counts_artifacts_eatf_and_caveat(self) -> None:
        index = self.load_json(INDEX_PATH)
        required_count_fields = {
            "pointer_attempts",
            "fetched_content_files",
            "fetch_errors",
            "normalized_xml_artifacts",
            "normalization_errors",
            "diff_change_count",
            "alert_entry_count",
        }
        required_diff_classes = {
            "listed_document_added",
            "listed_document_removed",
            "normalized_hash_changed",
            "summary_field_changed",
            "provider_inventory_changed",
            "service_inventory_changed",
            "provider_service_detail_changed",
        }
        for run in index["runs"]:
            self.assertRegex(run["date"], r"^20\d\d-\d\d-\d\d$")
            self.assertTrue(required_count_fields.issubset(run["counts"].keys()), run["date"])
            self.assertTrue(required_diff_classes.issubset(run["diff_classes"].keys()), run["date"])
            self.assertIn("snapshot_manifest", run["artifacts"], run["date"])
            self.assertIn("diff", run["artifacts"], run["date"])
            self.assertIn("status", run["eatf"], run["date"])
            self.assertIn("not trusted-list validation", run["caveat"], run["date"])


if __name__ == "__main__":
    unittest.main()
