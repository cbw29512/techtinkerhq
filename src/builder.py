"""Atomic, preview-first static website build; no external network calls."""
from __future__ import annotations
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape
from .schema import read_data
from .layout import layout, DOMAIN
from .content_render import article
from .pages import home, guide_index, info_page

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


def put(root: Path, path: str, content: str) -> None:
    try:
        target = root / (path.strip('/') + '/index.html') if path != '/' and not path.endswith('.html') else (root / ('index.html' if path == '/' else path.lstrip('/')))
        if not target.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Invalid site target: {path}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    except Exception:
        LOG.exception('Failed writing route %s', path)
        raise


def build(root: Path = ROOT, mode: str = 'preview') -> dict:
    if mode not in {'preview', 'production'}:
        raise ValueError('Unknown release mode')
    if mode == 'production' and os.getenv('RELEASE_APPROVED') != 'true':
        raise ValueError('Production blocked. Set RELEASE_APPROVED=true only after staging and DNS audit')
    doc, legacy = read_data(root)
    posts = doc['articles']
    output = root / 'dist'
    staging = root / 'dist.building'
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    try:
        shutil.copytree(root / 'assets', staging / 'assets', dirs_exist_ok=True)
        put(staging, '/', home(posts, mode))
        put(staging, '/guides/', guide_index(posts, mode))
        routes = ['/', '/guides/', '/about/', '/standards/', '/privacy/', '/disclosure/']
        for p in posts:
            path = '/guides/' + p['slug'] + '/'
            put(staging, path, article(p, mode))
            routes.append(path)
        for name in ('about', 'standards', 'privacy', 'disclosure'):
            put(staging, f'/{name}/', info_page(name, mode))
        put(staging, '/404.html', layout('Page not found', 'The page you requested was not found.', '/404.html', '<div class="container prose-wrap"><h1>That page has moved.</h1><p>Explore our current verified guides instead.</p><a class="button button-dark" href="/guides/">View guides</a></div>', 'preview'))
        redirects = [f"{r['source']}  {r['target']}  301" for r in legacy['paths']]
        (staging / '_redirects').write_text('\n'.join(redirects)+'\n', encoding='utf-8')
        (staging / '_headers').write_text((root / '_headers').read_text(encoding='utf-8'),encoding='utf-8')
        (staging / 'robots.txt').write_text('User-agent: *\n'+('Disallow: /\n' if mode == 'preview' else f'Allow: /\nSitemap: {DOMAIN}/sitemap.xml\n'),encoding='utf-8')
        (staging / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+xml_escape(DOMAIN+route)+'</loc></url>\n' for route in sorted(routes))+'</urlset>\n', encoding='utf-8')
        report = {'mode':mode,'published_verified_articles':len(posts),'legacy_redirects':len(redirects),'paths':routes,'launch_approved':mode=='production','source_export_included_in_public_site':False}
        (staging / 'build-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
        LOG.info('Generated %d guides, %d redirects in %s mode',len(posts),len(redirects),mode)
        return report
    except Exception:
        LOG.exception('Site build aborted without modifying DNS or hosting')
        shutil.rmtree(staging,ignore_errors=True)
        raise


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['preview','production'], default='preview')
    args = p.parse_args()
    try:
        build(mode=args.mode)
        return 0
    except Exception:
        LOG.exception('Build failed: existing deploy unchanged')
        return 1


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    sys.exit(main())
