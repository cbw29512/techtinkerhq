"""Data schema and state validation for source-bound draft generation."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

LOG = logging.getLogger(__name__)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Trusted documentation roots. Never accept arbitrary model-supplied URLs.
OFFICIAL_SOURCE_PATHS = (
    ("github.com", "/proxmox/pve-docs/"),
    ("docs.docker.com", "/engine/storage/"),
    ("ubuntu.com", "/server/docs/how-to/backups/"),
    ("docs.github.com", "/en/"),
)
MODEL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "title": {"type": "string"}, "description": {"type": "string"},
        "dek": {"type": "string"}, "reading_minutes": {"type": "integer"},
        "sections": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "heading": {"type": "string"},
                "paragraphs": {"type": "array", "items": {"type": "string"}},
                "bullets": {"type": "array", "items": {"type": "string"}},
                "evidence_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["heading", "paragraphs", "bullets", "evidence_ids"],
        }},
    },
    "required": ["title", "description", "dek", "reading_minutes", "sections"],
}


def next_topic(root: Path) -> dict | None:
    """Pick a unique curated topic; never ask an AI to choose its own evidence."""
    try:
        topics = json.loads((root / "content/draft-topics.json").read_text())
        queue = json.loads((root / "content/publish-queue.json").read_text())
        public = json.loads((root / "content/articles.json").read_text())
        if topics.get("schema_version") != 1 or queue.get("schema_version") != 1:
            raise ValueError("Unsupported topic/queue schema")
        taken = {x["slug"] for x in queue["items"] + public["articles"]}
        for item in topics.get("topics", []):
            slug = item.get("slug", "")
            if not SLUG.fullmatch(slug):
                raise ValueError("Invalid curated topic slug")
            if slug in taken:
                continue
            facts = item.get("facts", [])
            ids = [f.get("id") for f in facts]
            if len(facts) < 3 or len(ids) != len(set(ids)):
                raise ValueError("Evidence packet requires unique fact identifiers")
            for f in facts:
                if not SLUG.fullmatch(f["id"]) or not 25 <= len(f["text"]) <= 500:
                    raise ValueError("Invalid evidence fact")
            for source in item.get("sources", []):
                url = urlparse(source.get("url", ""))
                if url.scheme != "https" or url.hostname != "github.com" or not url.path.startswith("/proxmox/pve-docs/"):
                    raise ValueError("This pilot only accepts official Proxmox documentation")
            if not item.get("sources") or not item.get("focus"):
                raise ValueError("Topic requires sources and editorial focus")
            return item
        return None
    except Exception:
        LOG.exception("Curated topic selection failed")
        raise


def validate_draft(topic: dict, output: dict) -> dict:
    """Constrain model prose and identifiers before touching the review queue."""
    try:
        if not isinstance(output, dict) or set(output) != set(MODEL_SCHEMA["required"]):
            raise ValueError("Unexpected generated document fields")
        for field, limit in (("title", 100), ("description", 170), ("dek", 300)):
            value = output[field]
            if not isinstance(value, str) or not 25 <= len(value.strip()) <= limit:
                raise ValueError(f"Invalid generated {field}")
        if type(output["reading_minutes"]) is not int or not 2 <= output["reading_minutes"] <= 12:
            raise ValueError("Invalid reading duration")
        sections = output["sections"]
        if not isinstance(sections, list) or not 3 <= len(sections) <= 6:
            raise ValueError("Three to six sections required")
        allowed = {f["id"] for f in topic["facts"]}
        for section in sections:
            if not isinstance(section, dict) or set(section) != set(MODEL_SCHEMA["properties"]["sections"]["items"]["required"]):
                raise ValueError("Unrecognized section format")
            if not isinstance(section["heading"], str) or not 5 <= len(section["heading"]) <= 100:
                raise ValueError("Invalid section heading")
            if not isinstance(section["paragraphs"], list) or not 1 <= len(section["paragraphs"]) <= 4:
                raise ValueError("Invalid paragraphs")
            if not isinstance(section["bullets"], list) or len(section["bullets"]) > 6:
                raise ValueError("Invalid bullet list")
            if not isinstance(section["evidence_ids"], list) or not section["evidence_ids"] or not set(section["evidence_ids"]) <= allowed:
                raise ValueError("Section lacks matching curated evidence")
            for p in section["paragraphs"] + section["bullets"]:
                if not isinstance(p, str) or not 15 <= len(p) <= 750 or re.search(r"(?i)https?://|<[^>]+>|\bexample\.com\b|\bXXXXXXXX\b", p):
                    raise ValueError("Unsupported external URL, HTML, or unsafe paragraph")
        return {
            "id": topic["id"], "slug": topic["slug"], "status": "review_needed",
            "category": topic["category"], "kind": topic["kind"],
            "reading_minutes": output["reading_minutes"], "featured": False,
            "title": output["title"], "description": output["description"],
            "dek": output["dek"], "sections": sections, "sources": topic["sources"],
        }
    except Exception:
        LOG.exception("Rejected AI draft before queue insertion")
        raise
