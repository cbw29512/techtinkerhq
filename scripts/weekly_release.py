"""Publish one explicitly reviewed article from the weekly queue, or do nothing.

Data: content/publish-queue.json schema_version=1; queue states:
review_needed -> approved -> published. A release never creates approval.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from src.schema import read_data

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATES = {"review_needed", "approved", "published"}


def _json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        LOG.exception("Cannot load required publication data: %s", path)
        raise


def _write(path: Path, data: dict) -> None:
    """Replace a JSON file through a sibling temp file, never partial text."""
    temp = path.with_suffix(path.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp, path)
    except Exception:
        LOG.exception("Cannot safely update %s", path)
        temp.unlink(missing_ok=True)
        raise


def release(root: Path = ROOT, apply: bool = False) -> dict:
    """Fail on mismatches; at most one already-approved queue item per run."""
    try:
        queue_path = root / "content" / "publish-queue.json"
        article_path = root / "content" / "articles.json"
        queue = _json(queue_path)
        articles, archive = read_data(root)
        if queue.get("schema_version") != 1 or not isinstance(queue.get("items"), list):
            raise ValueError("Unsupported publishing queue schema")

        existing = {a["slug"] for a in articles["articles"]}
        queued = set()
        candidates = []
        for item in queue["items"]:
            slug = item.get("slug")
            state = item.get("status")
            article = item.get("article", {})
            if not isinstance(slug, str) or not slug or slug in queued:
                raise ValueError("Duplicate or missing queue slug")
            if state not in STATES or article.get("slug") != slug:
                raise ValueError(f"Invalid queue state or article identity: {slug}")
            queued.add(slug)
            if state == "published" and slug not in existing:
                raise ValueError(f"Published queue item missing from website: {slug}")
            if state == "approved":
                if slug in existing:
                    raise ValueError(f"Approved queue item already on website: {slug}")
                review = item.get("review", {})
                if (not isinstance(review.get("verified_by"), str)
                    or not review["verified_by"].strip()
                    or not DATE.fullmatch(review.get("verified_at", ""))
                    or review.get("sources_checked") is not True):
                    raise ValueError(f"Missing human verification for: {slug}")
                candidates.append(item)

        if not candidates:
            LOG.info("No approved articles; no website or queue changes")
            return {"changed": False, "slug": None}
        item = candidates[0]
        copy = dict(item["article"])
        copy["status"] = "approved"
        proposed = {**articles, "articles": [*articles["articles"], copy]}

        # Run the exact site schema against proposed content before writing.
        with TemporaryDirectory(prefix="tthq-release-") as tmp:
            temp_root = Path(tmp)
            (temp_root / "content").mkdir()
            (temp_root / "archive").mkdir()
            _write(temp_root / "content" / "articles.json", proposed)
            _write(temp_root / "archive" / "legacy-map.json", archive)
            read_data(temp_root)

        if not apply:
            LOG.info("Dry run: next reviewed article is %s", item["slug"])
            return {"changed": False, "slug": item["slug"], "eligible": True}

        # GitHub Actions runs tests before committing either changed file.
        item["status"] = "published"
        item["published_at"] = datetime.now(timezone.utc).isoformat()
        _write(article_path, proposed)
        _write(queue_path, queue)
        LOG.info("Released reviewed article to Git workspace: %s", item["slug"])
        return {"changed": True, "slug": item["slug"]}
    except Exception:
        LOG.exception("Weekly publication failed closed")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Review-gated weekly guide publisher")
    parser.add_argument("--apply", action="store_true", help="Update source files for a scheduled run")
    args = parser.parse_args()
    try:
        result = release(apply=args.apply)
        LOG.info("Weekly release result: %s", result)
        return 0
    except Exception:
        LOG.exception("No publication was committed")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
