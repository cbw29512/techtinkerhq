"""Fail closed on broken internal URLs, metadata, staging safety, and legacy paths."""
from __future__ import annotations
import json
import logging
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from .builder import ROOT

LOG = logging.getLogger(__name__)


def thumbnail_dimensions(path: Path) -> tuple[int, int]:
    """Read the lossily encoded WebP image header using only the Python stdlib."""
    try:
        with path.open("rb") as handle:
            header = handle.read(32)
        if (len(header) < 30 or header[:4] != b"RIFF"
                or header[8:12] != b"WEBP" or header[12:16] != b"VP8 "):
            raise ValueError(f"Unsupported thumbnail file/header: {path.name}")
        width = int.from_bytes(header[26:28], "little") & 0x3fff
        height = int.from_bytes(header[28:30], "little") & 0x3fff
        if width == 0 or height == 0:
            raise ValueError(f"Empty thumbnail dimensions: {path.name}")
        return width, height
    except Exception:
        LOG.exception("Cannot verify visual dimensions for %s", path)
        raise


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.images = []
        self.robots = ''
        self.titles = 0
        self.headings = 0
        self.descriptions = 0
        self.canonicals = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if tag == 'h1': self.headings += 1
        if tag == 'title': self.titles += 1
        if tag == 'meta' and a.get('name') == 'robots': self.robots = a.get('content', '')
        if tag == 'meta' and a.get('name') == 'description': self.descriptions += 1
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals += 1
        if tag == 'img' and a.get('src', '').startswith('/assets/thumbnails/'):
            self.images.append(a['src'])
        if tag in ('a','link','script','img'):
            for key in ('href', 'src'):
                if a.get(key, '').startswith('/') and not a[key].startswith('//'):
                    self.links.append(a[key])


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    try:
        dist = root / 'dist'
        report = json.loads((dist/'build-report.json').read_text())
        pages = list(dist.rglob('*.html'))
        if len(pages) != len(report['paths']) + 1:
            errors.append(f'Route count mismatch: {len(pages)} files for {len(report["paths"])} public routes')
        checked_images = set()
        for item in pages:
            content = item.read_text(encoding='utf-8')
            scan = PageScan()
            scan.feed(content)
            if content.count('<html lang="en"') != 1:
                errors.append(f'{item}: missing language')
            if (scan.titles,scan.headings,scan.descriptions,scan.canonicals) != (1,1,1,1):
                errors.append(f'{item}: missing/duplicate metadata or h1')
            if report['mode'] == 'preview' and 'noindex' not in scan.robots:
                errors.append(f'{item}: preview page missing noindex')
            for url in scan.links:
                decoded = unquote(urlparse(url).path)
                if '\x00' in decoded or '/../' in decoded:
                    errors.append(f'{item}: unsafe local link {url}'); continue
                path = dist/decoded.lstrip('/')
                if decoded == '/': path = dist/'index.html'
                elif decoded.endswith('/'): path = path/'index.html'
                if not path.is_file(): errors.append(f'{item}: missing asset {url}')
            # Reject thumbnails too small for high-DPI cards; verify source quality separately.
            for source in scan.images:
                clean_source = unquote(urlparse(source).path)
                if clean_source in checked_images:
                    continue
                checked_images.add(clean_source)
                image_file = dist / clean_source.lstrip('/')
                if image_file.is_file():
                    try:
                        width, height = thumbnail_dimensions(image_file)
                        if width < 1000 or height < 500:
                            errors.append(f'{item}: low-resolution image {source} ({width}x{height})')
                    except Exception:
                        errors.append(f'{item}: invalid or unreadable WebP image {source}')
            if re.search(r'(?i)XXXXXXXX|lorem ipsum|personal hands.on review|demo checkout',content):
                errors.append(f'{item}: suspicious placeholder/claim')
        redirects = (dist/'_redirects').read_text(encoding='utf-8').splitlines()
        if len(redirects) != report['legacy_redirects']:
            errors.append('Legacy redirect count mismatch')
        if not all(line.endswith('  301') for line in redirects):
            errors.append('Invalid legacy redirect status')
        robots = (dist/'robots.txt').read_text()
        if report['mode']=='preview' and 'Disallow: /' not in robots:
            errors.append('Preview robots did not block crawlers')
        if report['mode']=='production' and 'Disallow: /' in robots:
            errors.append('Production robots blocks crawlers')
        for file in ('assets/favicon.svg','assets/social.svg','assets/filters.js','_headers','sitemap.xml'):
            if not (dist/file).is_file(): errors.append(f'Missing deploy asset: {file}')
        if any(dist.rglob('*.xml')) and (dist/'source').exists():
            errors.append('Raw WordPress export was copied into production')
        return errors
    except Exception:
        LOG.exception('Static site QA could not complete')
        return ['QA crashed; deployment must stop']


def main() -> int:
    problems = validate()
    if problems:
        for message in problems[:40]: LOG.error(message)
        return 1
    LOG.info('Site QA passed: pages, assets, metadata, redirects, and preview safety')
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    sys.exit(main())
