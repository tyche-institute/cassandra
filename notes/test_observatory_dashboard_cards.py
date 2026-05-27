#!/usr/bin/env python3
"""Smoke tests for Cassandra public dashboard cards."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from scripts.build_observatory_index import CAVEAT, build_index


REQUIRED_CARDS = {
    "claim-boundary.json",
    "latest-run.json",
    "eatf-receipt.json",
    "aggregate-diffs.json",
    "caveat.json",
}


FORBIDDEN_POSITIVE_PATTERNS = [
    "legal status verified",
    "signature validity verified",
    "supervisory approval granted",
    "is a compliance judgment",
    "issues public alerts",
]


def assert_no_positive_overclaim(obj: object) -> None:
    text = json.dumps(obj, sort_keys=True).lower()
    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        assert pattern not in text, pattern


def main() -> None:
    workspace = pathlib.Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="cassandra-dashboard-cards-") as tmp:
        public_dir = pathlib.Path(tmp) / "public"
        index = build_index(workspace, public_dir, workspace / "notes/aggregate-results-2026-05-27-output.json")
        cards_dir = public_dir / "data" / "cards"
        assert cards_dir.is_dir(), "cards directory should be generated"
        card_names = {path.name for path in cards_dir.glob("*.json")}
        assert REQUIRED_CARDS <= card_names, sorted(REQUIRED_CARDS - card_names)

        for card_name in REQUIRED_CARDS:
            card = json.loads((cards_dir / card_name).read_text(encoding="utf-8"))
            assert card["schema"] == "urn:tyche:cassandra:observatory-card:0.1"
            assert card["project"] == "cassandra"
            assert card["caveat"] == CAVEAT
            assert card.get("not_a")
            assert "trusted-list validation" in card["not_a"]
            assert "public alerting" in card["not_a"]
            assert_no_positive_overclaim(card)

        cards_index = json.loads((cards_dir / "index.json").read_text(encoding="utf-8"))
        assert cards_index["schema"] == "urn:tyche:cassandra:observatory-card-index:0.1"
        assert cards_index["card_count"] == len(REQUIRED_CARDS)
        assert {card["path"] for card in cards_index["cards"]} == {f"data/cards/{name}" for name in REQUIRED_CARDS}
        assert all(card.get("sha256") and len(card["sha256"]) == 64 for card in cards_index["cards"])
        assert index["dashboard_cards"]["card_count"] == len(REQUIRED_CARDS)
        assert index["dashboard_cards"]["index"] == "data/cards/index.json"
        assert index["dashboard_cards"]["index_sha256"] == cards_index["sha256"]

        latest_run_card = json.loads((cards_dir / "latest-run.json").read_text(encoding="utf-8"))
        assert latest_run_card["title"] == "Latest Cassandra run"
        assert latest_run_card["data"]["date"] == index["latest_date"]
        assert latest_run_card["data"]["diff_change_count"] == index["runs"][-1]["counts"]["diff_change_count"]

        eatf_card = json.loads((cards_dir / "eatf-receipt.json").read_text(encoding="utf-8"))
        assert eatf_card["data"]["status"] == index["runs"][-1]["eatf"]["status"]
        assert "package bytes" in eatf_card["interpretation"]
        assert "legal-status determination" in eatf_card["not_a"]

        aggregate_card = json.loads((cards_dir / "aggregate-diffs.json").read_text(encoding="utf-8"))
        assert aggregate_card["data"]["diff_change_count"] == index["aggregate"]["totals"]["diff_change_count"]
        assert aggregate_card["data"]["diff_class_totals"] == index["aggregate"]["diff_class_totals"]

        # Ensure the temp cards are self-contained and no source tree card directory was needed.
        assert not (workspace / "observatory" / "public" / "data" / "cards" / "__tmp_marker__").exists()

        print(
            json.dumps(
                {
                    "status": "ok",
                    "generated_card_count": len(REQUIRED_CARDS),
                    "cards_index_sha256": cards_index["sha256"],
                    "checked_boundary_caveat": CAVEAT,
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
