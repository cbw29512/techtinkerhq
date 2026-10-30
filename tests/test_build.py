"""Unit tests of validation contracts and production fail-closed behavior."""
import json
import logging
import tomllib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.builder import build
from src.qa import validate
from src.schema import read_data

ROOT = Path(__file__).resolve().parents[1]


class SiteContractTests(unittest.TestCase):
    def test_netlify_production_context_is_isolated_from_previews(self):
        """Avoid accidentally indexing draft previews or deploying noindex production."""
        try:
            config = tomllib.loads((ROOT / 'netlify.toml').read_text(encoding='utf-8'))
            preview = config['build']['command']
            production = config['context']['production']['command']
            self.assertIn('--mode preview', preview)
            self.assertNotIn('RELEASE_APPROVED=true', preview)
            self.assertIn('RELEASE_APPROVED=true', production)
            self.assertIn('--mode production', production)
            self.assertIn('python3 -m src.qa', production)
            self.assertIn("grep -q 'index,follow' dist/index.html", production)
            self.assertIn("! grep -q 'noindex' dist/index.html", production)
        except Exception:
            logging.getLogger(__name__).exception('Netlify context production contract invalid')
            raise

    def test_source_schema_has_three_approved_guides(self):
        data, archive = read_data(ROOT)
        self.assertGreaterEqual(len(data['articles']), 3)
        self.assertEqual(len(archive['paths']), 15)

    def test_legacy_paths_unique_and_targeted(self):
        _, archive = read_data(ROOT)
        self.assertEqual(len({p['source'] for p in archive['paths']}), 15)
        self.assertTrue(all(p['target'].startswith(('/guides/', '/about/')) for p in archive['paths']))

    def test_production_blocked_without_explicit_approval(self):
        with patch.dict(os.environ, {'RELEASE_APPROVED':'false'}):
            with self.assertRaisesRegex(ValueError, 'Production blocked'):
                build(ROOT, 'production')

    def test_preview_build_and_static_qa(self):
        output = build(ROOT, 'preview')
        self.assertEqual(output['legacy_redirects'],15)
        self.assertEqual(validate(ROOT), [])

    def test_homepage_displays_approved_cards_before_secondary_sections(self):
        """Keep the browsable guide cards prominent without changing review state."""
        try:
            # The fixture reads the real approved article list, never the draft queue.
            articles, _ = read_data(ROOT)
            build(ROOT, 'preview')
            homepage = (ROOT / 'dist' / 'index.html').read_text(encoding='utf-8')
            self.assertIn('class="cards-grid home-cards"', homepage)
            self.assertLess(
                homepage.index('class="cards-grid home-cards"'),
                homepage.index('class="container value-section"'),
            )
            self.assertNotIn('class="hero-visual"', homepage)
            for item in articles['articles']:
                self.assertIn('/guides/' + item['slug'] + '/', homepage)
            # Draft previews must stay blocked from indexing despite the redesign.
            self.assertIn('noindex,nofollow', homepage)
        except Exception:
            logging.getLogger(__name__).exception('Card-first homepage regression failed')
            raise

    def test_homepage_has_one_standards_navigation_link(self):
        # Keep the editorial standard accessible without three repeated homepage CTAs.
        build(ROOT, 'preview')
        homepage = (ROOT/'dist'/'index.html').read_text(encoding='utf-8')
        self.assertEqual(homepage.count('href="/standards/"'), 1)
        self.assertIn('>How we verify</a>', homepage)
        self.assertTrue((ROOT/'dist'/'standards'/'index.html').is_file())

    def test_preview_content_is_not_indexable(self):
        build(ROOT, 'preview')
        self.assertIn('noindex', (ROOT/'dist'/'index.html').read_text())
        self.assertIn('Disallow: /', (ROOT/'dist'/'robots.txt').read_text())

    def test_safe_evidence_links_and_metadata(self):
        data, _ = read_data(ROOT)
        for article in data['articles']:
            self.assertGreater(len(article['sources']), 0)
            self.assertLessEqual(len(article['description']), 170)
            self.assertTrue(all(s['url'].startswith('https://') for s in article['sources']))

    def test_imported_wordpress_raw_export_is_not_shipped(self):
        build(ROOT, 'preview')
        self.assertFalse((ROOT/'dist'/'source').exists())
        self.assertFalse(any((ROOT/'dist').rglob('wordpress.xml')))

    def test_release_opt_in_produces_indexable_documents(self):
        with patch.dict(os.environ, {'RELEASE_APPROVED':'true'}):
            try:
                rep = build(ROOT, 'production')
                self.assertTrue(rep['launch_approved'])
                self.assertIn('index,follow', (ROOT/'dist'/'index.html').read_text())
                self.assertEqual(validate(ROOT), [])
            finally:
                build(ROOT, 'preview')


if __name__ == '__main__':
    unittest.main()
