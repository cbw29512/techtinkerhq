"""Checks that weekly publishing never promotes a draft without approval."""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.weekly_release import release
from src.schema import read_data

LOG = logging.getLogger(__name__)
REPO = Path(__file__).resolve().parents[1]


class WeeklyReleaseTests(unittest.TestCase):
    def setUp(self):
        try:
            self.temp = tempfile.TemporaryDirectory(prefix="tthq-weekly-test-")
            self.root = Path(self.temp.name)
            (self.root / "content").mkdir()
            (self.root / "archive").mkdir()
            for path in ("content/articles.json", "content/publish-queue.json",
                         "archive/legacy-map.json"):
                shutil.copy2(REPO / path, self.root / path)
            # Use a synthetic candidate, independent of previous real releases.
            queue_path = self.root / "content/publish-queue.json"
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            candidate = queue["items"][0]
            candidate["slug"] = "automation-regression-guide"
            candidate["id"] = "automation-regression-guide"
            candidate["status"] = "review_needed"
            candidate["review"] = {
                "verified_by": "", "verified_at": "", "sources_checked": False,
            }
            candidate["article"]["id"] = "automation-regression-guide"
            candidate["article"]["slug"] = "automation-regression-guide"
            candidate["article"]["status"] = "review_needed"
            queue["items"] = [candidate]
            queue_path.write_text(json.dumps(queue), encoding="utf-8")
        except Exception:
            LOG.exception("Could not prepare weekly release fixture")
            raise

    def tearDown(self):
        try:
            self.temp.cleanup()
        except Exception:
            LOG.exception("Could not clean weekly release fixture")
            raise

    def _approve(self):
        try:
            path = self.root / "content/publish-queue.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            first = data["items"][0]
            first["status"] = "approved"
            first["review"] = {
                "verified_by": "human-editor",
                "verified_at": "2026-10-30",
                "sources_checked": True,
            }
            path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            LOG.exception("Could not build approved test fixture")
            raise

    def test_draft_never_publishes(self):
        try:
            baseline = (self.root / "content/articles.json").read_bytes()
            self.assertEqual(release(self.root, apply=True)["changed"], False)
            self.assertEqual(baseline, (self.root / "content/articles.json").read_bytes())
        except Exception:
            LOG.exception("Unapproved draft was incorrectly released")
            raise

    def test_missing_review_proof_blocks_publication(self):
        try:
            queue_path = self.root / "content/publish-queue.json"
            data = json.loads(queue_path.read_text())
            data["items"][0]["status"] = "approved"
            queue_path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Missing human verification"):
                release(self.root, apply=True)
        except Exception:
            LOG.exception("Review requirement regression")
            raise

    def test_approved_content_releases_once(self):
        try:
            self._approve()
            baseline, _ = read_data(self.root)
            original_count = len(baseline["articles"])
            dry = release(self.root, apply=False)
            self.assertEqual(dry["changed"], False)
            actual = release(self.root, apply=True)
            self.assertTrue(actual["changed"])
            site, _ = read_data(self.root)
            self.assertEqual(len(site["articles"]), original_count + 1)
            self.assertEqual(site["articles"][-1]["status"], "approved")
            queue = json.loads((self.root / "content/publish-queue.json").read_text())
            self.assertEqual(queue["items"][0]["status"], "published")
            self.assertEqual(release(self.root, apply=True)["changed"], False)
        except Exception:
            LOG.exception("Weekly release was not idempotent")
            raise

    def test_duplicate_slug_rejected(self):
        try:
            self._approve()
            path = self.root / "content/publish-queue.json"
            data = json.loads(path.read_text())
            data["items"][0]["slug"] = "10gbe-switch-homelab-checklist"
            data["items"][0]["article"]["slug"] = "10gbe-switch-homelab-checklist"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "already on website"):
                release(self.root, apply=True)
        except Exception:
            LOG.exception("Duplicate slug release protection regressed")
            raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
