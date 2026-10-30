"""Accessible shared shell, metadata and permanent navigation."""
from __future__ import annotations
import html
import json
from datetime import date

BRAND = 'TechTinkerer HQ'
DOMAIN = 'https://techtinkererhq.com'


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def layout(title: str, description: str, path: str, body: str, mode: str,
           page_type: str = 'WebPage', extra_head: str = '') -> str:
    try:
        noindex = mode != 'production'
        canonical = DOMAIN + path
        metadata = {'@context': 'https://schema.org', '@type': page_type,
                    'name': title, 'url': canonical, 'description': description}
        jsonld = json.dumps(metadata, ensure_ascii=False).replace('<', '\\u003c')
        return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101a29">
<title>{esc(title)} | {BRAND}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="{'noindex,nofollow' if noindex else 'index,follow,max-image-preview:large'}">
<link rel="canonical" href="{esc(canonical)}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="{'article' if page_type == 'Article' else 'website'}">
<meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{DOMAIN}/assets/social.svg"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/base.css"><link rel="stylesheet" href="/assets/layout.css">
<link rel="stylesheet" href="/assets/components.css"><link rel="stylesheet" href="/assets/pages.css">
<script type="application/ld+json">{jsonld}</script>{extra_head}
</head><body>
<a class="skip-link" href="#main">Skip to main content</a>
<div class="topline"><div class="container top-inner"><span>Clear specs. Useful context. No invented reviews.</span><a href="/standards/">Our editorial standard <span aria-hidden="true">↗</span></a></div></div>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="/" aria-label="TechTinkerer HQ home"><span class="brand-mark" aria-hidden="true">T<span class="mark-dot">.</span></span><span>TechTinkerer <em>HQ</em></span></a>
<nav aria-label="Main navigation"><ul><li><a href="/guides/">All guides</a></li><li><a href="/standards/">How we verify</a></li><li><a href="/about/">About</a></li></ul></nav>
</div></header>
{('<div class="preview-banner" role="status">Staging preview · Not approved for public launch</div>' if noindex else '')}
<main id="main">{body}</main>
<footer class="footer"><div class="container footer-grid">
<div><a class="brand footer-brand" href="/" aria-label="TechTinkerer HQ home"><span class="brand-mark" aria-hidden="true">T<span class="mark-dot">.</span></span><span>TechTinkerer <em>HQ</em></span></a>
<p>Making hardware specifications easier to understand—without pretending we tested what we didn't.</p></div>
<div><h2>Explore</h2><a href="/guides/">Tech guides</a><a href="/standards/">Editorial standards</a><a href="/about/">About the site</a></div>
<div><h2>Information</h2><a href="/privacy/">Privacy</a><a href="/disclosure/">Affiliate disclosure</a><a href="/sitemap.xml">Sitemap</a></div>
</div><div class="container footer-bottom"><span>© {date.today().year} {BRAND}. Independent technology explanations.</span><span>Built as a lightweight static website.</span></div></footer>
</body></html>'''
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Failed to render shared HTML shell')
        raise
