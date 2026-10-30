"""Render verified guides and browseable content cards from the schema."""
from __future__ import annotations
import json
import logging
from .layout import esc, layout, DOMAIN

LOG = logging.getLogger(__name__)


def card(item: dict, featured: bool = False) -> str:
    """Every published card uses the guide's reviewed, locally hosted visual."""
    try:
        href = '/guides/' + item['slug'] + '/'
        visual = item['visual']  # Validated by src.schema; never use generic art.
        return (f'<article class="guide-card {"wide-card" if featured else ""}" data-category="{esc(item["category"])}" '
                f'data-search="{esc(item["title"] + " " + item["description"] + " " + item["category"])}">'
                f'<div class="card-art"><img src="{esc(visual["src"])}" alt="{esc(visual["alt"])}" '
                f'width="760" height="380" loading="lazy" decoding="async">'
                '<span class="image-type" aria-hidden="true">Concept illustration</span></div>'
                f'<div class="card-content"><div class="card-top"><span class="category">{esc(item["category"])}</span>'
                f'<span>{int(item["reading_minutes"])} min read</span></div>'
                f'<h3><a href="{href}">{esc(item["title"])}</a></h3>'
                f'<p>{esc(item["description"])}</p>'
                f'<span class="card-link" aria-hidden="true">Read guide <span>↗</span></span></div></article>')
    except Exception:
        LOG.exception('Failed rendering card %s', item.get('id'))
        raise

def article(item: dict, mode: str) -> str:
    try:
        path = '/guides/' + item['slug'] + '/'
        sections = []
        for i, section in enumerate(item['sections'], 1):
            paragraphs = ''.join('<p>' + esc(p) + '</p>' for p in section.get('paragraphs', []))
            bullets = ('<ul class="article-list">' + ''.join('<li>' + esc(p) + '</li>' for p in section['bullets']) + '</ul>') if section.get('bullets') else ''
            sections.append(f'<section id="section-{i}" class="article-section"><h2>{esc(section["heading"])}</h2>{paragraphs}{bullets}</section>')
        toc = ''.join(f'<li><a href="#section-{i}">{esc(s["heading"])}</a></li>' for i, s in enumerate(item['sections'], 1))
        sources = ''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["name"])}</a></li>' for s in item['sources'])
        body = (f'<div class="container article-wrap"><div class="breadcrumbs"><a href="/">Home</a><span>/</span><a href="/guides/">Guides</a><span>/</span>{esc(item["category"])}</div>'
                f'<header class="article-header"><div class="article-meta"><span class="eyebrow">{esc(item["kind"])}</span><span class="meta-dot">•</span>'
                f'<span>{int(item["reading_minutes"])} minute read</span><span class="meta-dot">•</span><span>Verified Oct 30, 2026</span></div>'
                f'<h1>{esc(item["title"])}</h1><p class="article-dek">{esc(item["dek"])}</p>'
                '<div class="evidence-tag"><span aria-hidden="true">✓</span> Source-checked technical guide · Not a hands-on test</div></header>'
                f'<figure class="article-cover"><img src="{esc(item["visual"]["src"])}" alt="{esc(item["visual"]["alt"])}" width="760" height="380" loading="eager" decoding="async"><figcaption>AI-generated concept illustration; not an exact product photograph.</figcaption></figure>'
                '<div class="article-grid"><aside class="article-sidebar"><div class="toc"><h2>On this page</h2><ol>' + toc + '</ol></div></aside>'
                '<div class="article-main"><div class="article-disclosure"><strong>Editorial note</strong><p>We explain published product specifications. We have not independently bench-tested these products and currently show no affiliate purchase links.</p></div>'
                + ''.join(sections) + '<section class="sources"><h2>Manufacturer and project sources</h2><p>Product specifications can change by hardware revision or region. Check the linked documentation before buying.</p><ol>' + sources + '</ol></section>'
                '<div class="article-end"><strong>Make the spec sheet do the talking.</strong><p>More practical guidance, less guesswork.</p><a class="button button-dark" href="/guides/">Browse all guides <span aria-hidden="true">↗</span></a></div></div></div></div>')
        ld = {'@context':'https://schema.org','@type':'Article','headline':item['title'],'description':item['description'],
              'datePublished':'2026-10-30','dateModified':'2026-10-30','mainEntityOfPage':DOMAIN+path,
              'author':{'@type':'Organization','name':'TechTinkerer HQ'}, 'publisher':{'@type':'Organization','name':'TechTinkerer HQ'}}
        extra = '<script type="application/ld+json">'+json.dumps(ld).replace('<','\\u003c')+'</script>'
        return layout(item['title'], item['description'], path, body, mode, 'Article', extra)
    except Exception:
        LOG.exception('Failed rendering article %s', item.get('id'))
        raise
