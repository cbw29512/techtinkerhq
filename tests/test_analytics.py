"""Fail-closed GA4 tagging: no tracking in preview or before consent."""
import logging
import unittest
from pathlib import Path

from src.analytics import MEASUREMENT_ID, analytics_head, consent_banner, privacy_button
from src.layout import layout
from src.pages import info_page

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


class GoogleAnalyticsTests(unittest.TestCase):
    def test_preview_does_not_install_google_tag(self):
        try:
            page = layout('Preview', 'Test preview', '/', '<h1>Preview</h1>', 'preview')
            self.assertNotIn(MEASUREMENT_ID, page)
            self.assertNotIn('analytics-consent.js', page)
            self.assertNotIn('analytics-consent', page)
            self.assertNotIn('analytics-settings', page)
            self.assertIn('noindex,nofollow', page)
        except Exception:
            LOG.exception('Preview failed closed tracking regression')
            raise

    def test_production_includes_one_shared_opt_in_control(self):
        try:
            page = layout('Public', 'Test public', '/', '<h1>Public</h1>', 'production')
            self.assertEqual(page.count('data-ga4-id="' + MEASUREMENT_ID + '"'), 1)
            self.assertEqual(page.count('id="analytics-consent"'), 1)
            self.assertEqual(page.count('id="analytics-settings"'), 1)
            self.assertEqual(page.count('id="analytics-accept"'), 1)
            self.assertEqual(page.count('id="analytics-decline"'), 1)
            self.assertIn('index,follow', page)
            self.assertTrue(analytics_head('production'))
            self.assertTrue(consent_banner('production'))
            self.assertTrue(privacy_button('production'))
        except Exception:
            LOG.exception('Production GA4 opt-in controls regression')
            raise

    def test_privacy_policy_discloses_google_analytics(self):
        try:
            privacy = info_page('privacy', 'production')
            self.assertIn('Google Analytics', privacy)
            self.assertIn('Privacy choices', privacy)
            self.assertNotIn('We have not included advertising pixels or analytics scripts', privacy)
        except Exception:
            LOG.exception('Privacy notice is inconsistent with analytics')
            raise

    def test_csp_permits_google_tag_and_blocks_other_externals(self):
        try:
            headers = (ROOT / '_headers').read_text(encoding='utf-8')
            self.assertIn('https://www.googletagmanager.com', headers)
            self.assertIn('https://www.google-analytics.com', headers)
            self.assertIn("default-src 'none'", headers)
            self.assertIn("form-action 'self'", headers)
        except Exception:
            LOG.exception('Analytics CSP regression')
            raise

    def test_no_network_until_consent_in_local_script(self):
        try:
            script = (ROOT / 'assets/analytics-consent.js').read_text(encoding='utf-8')
            self.assertIn("if (choice === 'accepted')", script)
            self.assertIn('startAnalytics();', script)
            self.assertIn("window.gtag('consent', 'default'", script)
            self.assertIn("analytics_storage: 'denied'", script)
            self.assertIn("analytics_storage: 'granted'", script)
            self.assertIn("storeChoice('declined')", script)
            self.assertIn('window.location.reload()', script)
            self.assertIn('document.createElement(\'script\')', script)
        except Exception:
            LOG.exception('Consent-before-loading invariant broken')
            raise


if __name__ == '__main__':
    unittest.main()
