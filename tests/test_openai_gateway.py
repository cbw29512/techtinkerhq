"""Verify one-request OpenAI contract without using API credits."""
from __future__ import annotations

import json
import logging
import os
import unittest
from unittest.mock import patch

from scripts.draft_contract import next_topic
from scripts.openai_gateway import request_draft
from src.builder import ROOT

LOG = logging.getLogger(__name__)


class FakeReply:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return json.dumps(self.body).encode("utf-8")[:limit]


class OpenAIGatewayContractTests(unittest.TestCase):
    def test_requires_explicit_enable_and_credentials(self):
        topic = next_topic(ROOT)
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "false"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                request_draft(topic)
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "true"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "required"):
                request_draft(topic)

    def test_one_bounded_request_and_structured_output(self):
        topic = next_topic(ROOT)
        recorded = []
        def fake_http(request, timeout):
            recorded.append((json.loads(request.data), request.headers, timeout))
            return FakeReply({"status": "completed", "output": [
                {"type": "message", "content": [
                    {"type": "output_text", "text": '{"title":"sample"}'}]}]})
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "true",
                                        "OPENAI_API_KEY": "unit-test-key",
                                        "OPENAI_DRAFT_MODEL": "test-model"}):
            with patch("scripts.openai_gateway.urllib.request.urlopen", side_effect=fake_http):
                self.assertEqual(request_draft(topic)["title"], "sample")
        self.assertEqual(len(recorded), 1)
        payload, headers, timeout = recorded[0]
        self.assertFalse(payload["store"])
        self.assertEqual(payload["max_output_tokens"], 3500)
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["model"], "test-model")
        self.assertLessEqual(timeout, 90)

    def test_incomplete_response_fails_closed(self):
        topic = next_topic(ROOT)
        with patch.dict(os.environ, {"ENABLE_AI_DRAFTS": "true",
                                        "OPENAI_API_KEY": "unit-test-key",
                                        "OPENAI_DRAFT_MODEL": "test-model"}):
            with patch("scripts.openai_gateway.urllib.request.urlopen",
                       return_value=FakeReply({"status": "incomplete", "output": []})):
                with self.assertRaisesRegex(RuntimeError, "incomplete"):
                    request_draft(topic)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
