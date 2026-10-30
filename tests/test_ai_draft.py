"""Model-free tests for strict source grounding, opt-in and review-only state."""
from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ai_draft import generate
from scripts.draft_contract import next_topic, validate_draft
from src.schema import read_data

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


def fake_output(topic: dict) -> dict:
    """Fixture is not a real AI request or a researched article."""
    facts = [x["id"] for x in topic["facts"]]
    return {
        "title": "How to plan safer Proxmox network configuration changes",
        "description": "A structured introduction to Proxmox networking change risks, staged configuration, and safer recovery planning.",
        "dek": "Before changing host networking, understand bridges, staged interfaces, and your path back to the management console.",
        "reading_minutes": 4,
        "sections": [
            {"heading": "Confirm the network and management path", "paragraphs": [
                "Identify the current physical interface and virtual bridge so you know which traffic depends on the configuration."],
             "bullets": ["Document network connectivity before making a change."], "evidence_ids": [facts[0]]},
            {"heading": "Understand staged interface changes", "paragraphs": [
                "Proxmox uses a staged network configuration file and can apply the configuration through its interface."],
             "bullets": [], "evidence_ids": [facts[1], facts[2]]},
            {"heading": "Plan for a failed management connection", "paragraphs": [
                "A configuration error can cause remote loss of access, so check that a recovery console is available."],
             "bullets": ["Do not use network-disrupting legacy commands indiscriminately."],
             "evidence_ids": [facts[3], facts[4]]},
        ],
    }


class AIDraftingContractTests(unittest.TestCase):
    def setUp(self):
        try:
            self.tmp = tempfile.TemporaryDirectory(prefix="tthq-ai-test-")
            self.root = Path(self.tmp.name)
            for filename in ("content/draft-topics.json", "content/publish-queue.json",
                             "content/articles.json", "archive/legacy-map.json"):
                target = self.root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / filename, target)
            # Isolate the test topic so real AI draft merges cannot exhaust the fixture.
            topic_path = self.root / "content/draft-topics.json"
            topics = json.loads(topic_path.read_text(encoding="utf-8"))
            topics["topics"][0]["id"] = "synthetic-ai-draft-fixture"
            topics["topics"][0]["slug"] = "synthetic-ai-draft-fixture"
            topic_path.write_text(json.dumps(topics), encoding="utf-8")
        except Exception:
            LOG.exception("AI test fixture setup failed")
            raise

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except Exception:
            LOG.exception("AI fixture cleanup failed")
            raise

    def test_curated_topic_and_zero_cost_dry_run(self):
        self.assertIsNotNone(next_topic(self.root))
        with patch("scripts.ai_draft.request_draft", side_effect=AssertionError("API used")):
            self.assertTrue(generate(self.root, apply=False)["eligible"])

    def test_disabled_never_calls_a_model(self):
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "false"}):
            def forbidden(_):
                raise AssertionError("Unexpected API charge")
            self.assertTrue(generate(self.root, model_call=forbidden, apply=True)["disabled"])

    def test_generated_draft_cannot_publish_without_human_review(self):
        baseline, _ = read_data(self.root)
        calls = []
        def mock_model(topic):
            calls.append(topic["slug"])
            return fake_output(topic)
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "true"}):
            result = generate(self.root, model_call=mock_model, apply=True)
            self.assertTrue(result["changed"])
            self.assertEqual(len(calls), 1)
            queue = json.loads((self.root / "content/publish-queue.json").read_text())
            self.assertEqual(queue["items"][-1]["status"], "review_needed")
            self.assertFalse(queue["items"][-1]["review"]["sources_checked"])
            self.assertEqual(queue["items"][-1]["article"]["status"], "review_needed")
            public, _ = read_data(self.root)
            self.assertEqual(len(public["articles"]), len(baseline["articles"]))
            self.assertFalse(generate(self.root, model_call=mock_model, apply=True)["changed"])
            self.assertEqual(len(calls), 1)

    def test_unknown_evidence_ids_fail_closed(self):
        topic = next_topic(self.root)
        generated = fake_output(topic)
        generated["sections"][0]["evidence_ids"] = ["invented-doc"]
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_draft(topic, generated)

    def test_external_urls_or_html_rejected(self):
        topic = next_topic(self.root)
        generated = fake_output(topic)
        generated["sections"][0]["paragraphs"][0] += " See https://untrusted.invalid."
        with self.assertRaisesRegex(ValueError, "Unsupported external URL"):
            validate_draft(topic, generated)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
