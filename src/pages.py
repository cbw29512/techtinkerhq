"""Homepage, searchable guide index, and small informational pages."""
from __future__ import annotations
import logging
from .layout import layout, esc
from .content_render import card

LOG = logging.getLogger(__name__)


def home(articles: list[dict], mode: str) -> str:
    try:
        lead = articles[0]
        newest = ''.join(card(a) for a in reversed(articles[-6:]))
        body = '''<section class="hero"><div class="container hero-inner">
<div class="hero-copy"><p class="eyebrow"><span class="pulse-dot"></span> INDEPENDENT TECH EXPLAINERS</p>
<h1>Better tech decisions.<br><span>Less marketing noise.</span></h1>
<p>Before you buy the hardware, understand what the specs actually mean. Clear explanations, cited sources, and practical buying checklists.</p>
<div class="hero-actions"><a href="/guides/" class="button button-lime">Explore tech guides <span aria-hidden="true">↗</span></a></div>
<div class="hero-principles"><span><b aria-hidden="true">✓</b> Checked against documentation</span><span><b aria-hidden="true">✓</b> No invented hands-on tests</span></div>
</div>
<div class="hero-visual" aria-label="Our buying approach: identify the real requirement, verify the specifications, and decide with evidence"><div class="visual-header"><span class="visual-dots" aria-hidden="true">● ● ●</span><span>BUYER_DECISION.md</span><span class="visual-status">VERIFIED</span></div>
<div class="visual-body"><div class="visual-command">$ inspect --before-you-buy</div>
<div class="visual-step"><span>01</span><div><strong>Identify the requirement</strong><small>What problem needs solving?</small></div><em>✓</em></div>
<div class="visual-step"><span>02</span><div><strong>Verify the specifications</strong><small>Check the actual model and revision</small></div><em>✓</em></div>
<div class="visual-step"><span>03</span><div><strong>Compare the trade-offs</strong><small>Choose on evidence, not hype</small></div><em>✓</em></div>
<div class="visual-footer"><i></i> Quality gate: PASS</div></div></div>
</div></section>
<section class="container home-intro"><div><span class="eyebrow">THE LATEST</span><h2>Start with the facts.</h2><p>{len(articles)} source-checked guides, built to explain technical specifications and practical buying decisions.</p></div><a class="secondary-link" href="/guides/">View all guides <span aria-hidden="true">↗</span></a></section>
<section class="container"><div class="cards-grid">'''+newest+'''</div></section>
<section class="container value-section"><div class="value-heading"><span class="eyebrow">THE DIFFERENCE</span><h2>Honest guidance beats confident guesses.</h2></div><div class="value-grid">
<div><span class="value-number">01 /</span><h3>Real specifications</h3><p>We trace technical claims back to manufacturers or project documentation.</p></div>
<div><span class="value-number">02 /</span><h3>Clear caveats</h3><p>When a model revision or product detail matters, we say so explicitly.</p></div>
<div><span class="value-number">03 /</span><h3>No pretend testing</h3><p>Source-based explanations are identified as such. Hands-on results require actual testing.</p></div></div></section>
<section class="container closing-cta"><div><p class="eyebrow">BUY BETTER, NOT FASTER</p><h2>Know what matters before checkout.</h2><p>Read the checklist. Verify the model. Then make the call.</p></div><a class="button button-dark" href="/guides/">Read the guides <span aria-hidden="true">↗</span></a></section>'''
        body = body.replace('{len(articles)}', str(len(articles)))
        return layout('Tech guides without the guesswork', 'Independent, evidence-based technology buying guides. Clear hardware specifications, networking tips, and keyboard switch explainers.', '/', body, mode)
    except Exception:
        LOG.exception('Homepage generation failed')
        raise


def guide_index(articles: list[dict], mode: str) -> str:
    try:
        items = ''.join(card(article) for article in articles)
        body = '''<div class="container listing-wrap"><div class="breadcrumbs"><a href="/">Home</a><span>/</span>Guides</div>
<div class="listing-header"><span class="eyebrow">THE LIBRARY</span><h1>Tech guides, minus the fluff.</h1><p>Find the specification that matters. Every published guide includes the sources behind its claims.</p></div>
<div class="filterbar"><div class="search-wrap"><label for="guide-search">Search guides</label><div class="search-box"><span aria-hidden="true">⌕</span><input id="guide-search" type="search" placeholder="Try networking, Proxmox, switches..." autocomplete="off"></div></div>
<div class="filter-controls" role="group" aria-label="Filter by topic"><button class="filter active" type="button" data-filter="All" aria-pressed="true">All guides</button><button class="filter" type="button" data-filter="Networking" aria-pressed="false">Networking</button><button class="filter" type="button" data-filter="Keyboards" aria-pressed="false">Keyboards</button></div></div>
<p id="result-count" class="result-count" role="status" aria-live="polite">{len(articles)} guides</p><div id="guides-grid" class="cards-grid">'''+items+'''</div><p id="empty-state" class="empty-state" hidden>No guides match that search. Try another term or category.</p></div>
<script src="/assets/filters.js" defer></script>'''
        body = body.replace('{len(articles)}', str(len(articles)))
        return layout('All technology guides', 'Browse manufacturer-sourced networking, homelab, and keyboard guides. Search by topic and compare technical specifications.', '/guides/', body, mode)
    except Exception:
        LOG.exception('Guide directory generation failed')
        raise


def info_page(which: str, mode: str) -> str:
    try:
        pages = {
            'standards': ('How we verify technical claims', 'Our accuracy, sourcing, affiliate, and correction policies.', '''<p>Our goal is to reduce mistakes in buying advice. A page is not approved just because it reads confidently.</p><h2>What earns publication</h2><ol><li>Identify the exact model, revision, and user problem.</li><li>Check every material specification against manufacturer or project documentation.</li><li>Write clear limitations and include links readers can verify.</li><li>Confirm that product links go to the right item; do not use placeholder ASINs.</li><li>Run automated SEO, internal-link, accessibility, and duplication tests.</li><li>Require editorial approval before a production deployment.</li></ol><h2>What we do not claim</h2><p>Specification explainers are not described as hands-on reviews. We do not invent benchmarks, user quotes, prices, availability, or personal testing.</p><h2>Corrections</h2><p>Older WordPress posts contained technical errors and duplicates. Those posts are preserved in a recovery archive and excluded from the new recommendation list. Their former URLs lead to newly verified explanations when applicable.</p><h2>Advertising</h2><p>If we add affiliate links, any commission relationship will be disclosed clearly next to those links. No affiliate purchase links are currently active on this site.</p>'''),
            'about': ('About TechTinkerer HQ', 'Independent technology explainers, hardware basics, and buying checklists.', '''<p>TechTinkerer HQ helps people make sense of the practical details behind computer equipment and home-lab setups. We focus on <strong>what the equipment can actually do</strong>, not affiliate-driven rankings.</p><h2>Where we started</h2><p>This website replaces an earlier WordPress blog with duplicate articles and several incorrect product claims. The original content is retained for recovery, but published guides here are newly checked against source documentation.</p><h2>Our approach</h2><p>We explain specifications, identify compatibility traps, and label any limits to our evidence. We do not claim to have personally tested hardware without documented hands-on work.</p><p><a class="button button-dark" href="/standards/">See our verification process <span aria-hidden="true">↗</span></a></p>'''),
            'disclosure': ('Affiliate disclosure', 'How TechTinkerer HQ handles affiliate relationships and buying links.', '''<p><strong>There are currently no active affiliate purchase links on this website.</strong></p><p>We may earn commissions from qualifying purchases made through clearly identified links if affiliate links are introduced in the future. This will not change the buyer's price unless the merchant explicitly states otherwise.</p><p>If affiliate links are added, we will place disclosures near the relevant recommendation and identify the merchant. Inclusion in an article does not mean we personally tested an item.</p><p>For general guidance, see the <a href="https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking" target="_blank" rel="noopener noreferrer">FTC's Endorsement Guides FAQ</a>.</p>'''),
            'privacy': ('Privacy', 'Privacy and external-link information for this static website.', '''<p>This static version of TechTinkerer HQ does not offer user accounts, contact forms, or on-site comments. We have not included advertising pixels or analytics scripts in the packaged site.</p><p>When deployed, the hosting provider may process ordinary HTTP request details such as IP addresses and browser information for site operation and security. Refer to the provider's applicable policy for details.</p><p>Clicking external manufacturer or documentation links takes you to another service with its own privacy practices. We do not control those websites.</p><p>We will update this notice before introducing contact forms, analytics, advertising, or other data-collection features.</p>''')
        }
        title, desc, body = pages[which]
        return layout(title, desc, f'/{which}/', f'<div class="container prose-wrap"><div class="breadcrumbs"><a href="/">Home</a><span>/</span>{esc(title)}</div><span class="eyebrow">{esc(which.upper())}</span><h1>{esc(title)}</h1>{body}</div>', mode)
    except Exception:
        LOG.exception('Information page rendering failed: %s', which)
        raise
