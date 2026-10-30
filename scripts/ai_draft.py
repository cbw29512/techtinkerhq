"""Prepare one source-grounded draft PR payload; never approve or publish it."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.draft_contract import next_topic, validate_draft
from scripts.openai_gateway import request_draft
from src.schema import read_data

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


def generate(root: Path = ROOT, model_call=request_draft, apply: bool = False) -> dict:
    """Schema-first: no topic or missing opt-in means no billable API call."""
    try:
        topic = next_topic(root)
        if topic is None:
            LOG.info("All curated topics already queued; no model call")
            return {"changed": False, "slug": None}
        if not apply:
            LOG.info("Next draft topic %s (dry run; no API call)", topic["slug"])
            return {"changed": False, "slug": topic["slug"], "eligible": True}
        if os.getenv("ENABLE_AI_DRAFTS") != "true":
            LOG.info("AI drafting disabled; no model call")
            return {"changed": False, "slug": topic["slug"], "disabled": True}
        article = validate_draft(topic, model_call(topic))
        queue_path = root / "content/publish-queue.json"
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        public, legacy = read_data(root)
        item = {
            "id": topic["id"], "slug": topic["slug"],
            "status": "review_needed",
            "review": {"verified_by": "", "verified_at": "", "sources_checked": False, "visual_reviewed": False},
            "draft_evidence": {"facts": topic["facts"], "source_links": topic["sources"]},
            "article": article,
        }
        proposed = {**queue, "items": [*queue["items"], item]}
        # Existing release contract rejects duplicate slugs and unapproved publication.
        known = {a["slug"] for a in public["articles"]}
        queued = [a.get("slug") for a in proposed["items"]]
        if topic["slug"] in known or len(queued) != len(set(queued)):
            raise ValueError("Draft already published or queued")
        # Test candidate as though reviewed, without changing its actual review_needed state.
        # Temporary validation-only visual: never attach fake artwork to the
        # review queue. The human reviewer must provide the real asset later.
        validation_visual = {
            "src": "/assets/thumbnails/" + article["slug"] + ".webp",
            "alt": "Proposed conceptual illustration for the guide titled " + article["title"],
            "kind": "illustration",
        }
        copy = {**article, "status": "approved", "visual": validation_visual}
        with TemporaryDirectory(prefix="tthq-ai-validate-") as temp:
            path = Path(temp)
            (path / "content").mkdir()
            (path / "archive").mkdir()
            (path / "content/articles.json").write_text(
                json.dumps({**public, "articles": [*public["articles"], copy]}), encoding="utf-8")
            (path / "archive/legacy-map.json").write_text(
                json.dumps(legacy), encoding="utf-8")
            read_data(path)
        temp_path = queue_path.with_suffix(".json.tmp")
        try:
            temp_path.write_text(json.dumps(proposed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(temp_path, queue_path)
        finally:
            temp_path.unlink(missing_ok=True)
        LOG.info("Queued unapproved draft %s for manual review", topic["slug"])
        return {"changed": True, "slug": topic["slug"], "status": "review_needed"}
    except Exception:
        LOG.exception("AI draft generation failed closed; no publishing approval granted")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an unapproved technical draft")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--print-slug", action="store_true")
    args = parser.parse_args()
    try:
        topic = next_topic(ROOT)
        if args.print_slug:
            if topic:
                print(topic["slug"])
            return 0
        generate(ROOT, apply=args.apply)
        return 0
    except Exception:
        LOG.exception("No draft was published")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    sys.exit(main())
