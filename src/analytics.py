"""Production-only GA4 UI elements.

Schema: measurement ID is public; consent is kept in the browser, never on
the server. State = undecided, accepted, or declined.
"""
import logging

LOG = logging.getLogger(__name__)
MEASUREMENT_ID = 'G-SMB3Q8QMJ5'


def analytics_head(mode: str) -> str:
    try:
        if mode != 'production':
            return ''
        return (
            '<link rel="stylesheet" href="/assets/analytics-consent.css">\n'
            f'<script defer src="/assets/analytics-consent.js" data-ga4-id="{MEASUREMENT_ID}"></script>'
        )
    except Exception:
        LOG.exception('Analytics head generation failed')
        raise


def privacy_button(mode: str) -> str:
    try:
        return ('<button class="privacy-choice-link" id="analytics-settings" '
                'type="button">Privacy choices</button>' if mode == 'production' else '')
    except Exception:
        LOG.exception('Privacy choice button generation failed')
        raise


def consent_banner(mode: str) -> str:
    try:
        if mode != 'production':
            return ''
        return '''<section id="analytics-consent" class="analytics-consent"
aria-label="Optional analytics" tabindex="-1" hidden>
<div class="analytics-consent-inner">
<p><strong>Optional analytics.</strong> Allow optional traffic
measurement so we can improve this site. No Google Analytics tag loads
unless you choose Allow. <a href="/privacy/">Privacy details</a>.</p>
<div class="analytics-consent-actions">
<button id="analytics-accept" type="button">Allow analytics</button>
<button id="analytics-decline" type="button">Decline</button>
</div></div></section>'''
    except Exception:
        LOG.exception('Analytics consent banner generation failed')
        raise
