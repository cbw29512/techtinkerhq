"""Data and release-state validation. No page generation occurs in this module."""
from __future__ import annotations
import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

LOG = logging.getLogger(__name__)
_ALLOWED = {'www.tp-link.com', 'www.gateron.co', 'www.gateron.com', 'github.com'}
_SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
_BAD = re.compile(r'X{6,}|lorem ipsum|example\.com|(?i:sample page)|fake review')


def read_data(root: Path) -> tuple[dict, dict]:
    """Load source records; fail closed when schema or review state is invalid."""
    try:
        doc = json.loads((root / 'content' / 'articles.json').read_text(encoding='utf-8'))
        archive = json.loads((root / 'archive' / 'legacy-map.json').read_text(encoding='utf-8'))
        if doc.get('schema_version') != 2 or archive.get('schema_version') != 1:
            raise ValueError('Unsupported article or legacy mapping schema')
        seen = set()
        for item in doc.get('articles', []):
            slug = item.get('slug', '')
            if not _SLUG.fullmatch(slug) or slug in seen:
                raise ValueError(f'Unsafe or duplicate article slug: {slug!r}')
            seen.add(slug)
            if item.get('status') != 'approved':
                raise ValueError(f'Article {slug} not approved; publishing blocked')
            for field in ('title', 'description', 'dek', 'category', 'kind'):
                if not isinstance(item.get(field), str) or len(item[field].strip()) < 4:
                    raise ValueError(f'Article {slug} missing {field}')
            if len(item.get('description', '')) > 170:
                raise ValueError(f'Article {slug} SEO description is too long')
            if len(item.get('sources', [])) < 1 or len(item.get('sections', [])) < 2:
                raise ValueError(f'Article {slug} lacks cited research or sections')
            for source in item['sources']:
                url = urlparse(source.get('url', ''))
                if url.scheme != 'https' or url.hostname not in _ALLOWED:
                    raise ValueError(f'Article {slug} has unapproved evidence domain: {url.hostname}')
            raw = json.dumps(item)
            if _BAD.search(raw):
                raise ValueError(f'Article {slug} contains placeholder text')
            if any(x in raw.lower() for x in ('amzn.to/', 'amazon.com/dp/', 'ref=')):
                raise ValueError(f'Article {slug} has unverified affiliate links')
        sources = set()
        for redirect in archive.get('paths', []):
            old, new = redirect['source'], redirect['target']
            if old in sources or not old.startswith('/') or '..' in old:
                raise ValueError(f'Invalid or duplicate legacy path {old}')
            sources.add(old)
            if new not in {f'/guides/{s}/' for s in seen} | {'/about/'}:
                raise ValueError(f'Legacy redirect points to missing destination {new}')
        if len(seen) < 3 or len(sources) < 1:
            raise ValueError('Insufficient verified content or legacy redirects')
        return doc, archive
    except Exception:
        LOG.exception('Rejected incomplete or unsafe source records')
        raise
