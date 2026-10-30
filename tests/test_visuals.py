"""Visual publishing regression checks: subject relevance and no missing art."""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
import unittest
from pathlib import Path

from src.builder import build
from src.schema import read_data

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]


class ArticleVisualTests(unittest.TestCase):
    def test_every_approved_guide_has_a_distinct_local_image(self):
        try:
            doc, _ = read_data(ROOT)
            images = [x['visual'] for x in doc['articles']]
            self.assertEqual(len(images), len({x['src'] for x in images}))
            for visual in images:
                binary = ROOT / visual['src'].lstrip('/')
                self.assertTrue(binary.is_file(), binary)
                self.assertGreater(binary.stat().st_size, 1024)
                self.assertGreaterEqual(len(visual['alt']), 40)
            build(ROOT, mode='preview')
            html = (ROOT / 'dist' / 'index.html').read_text(encoding='utf-8')
            self.assertEqual(html.count('class="image-type"'), len(images))
            for visual in images:
                self.assertIn(visual['src'], html)
                self.assertIn(visual['alt'], html)
            self.assertNotIn('class="switch-box"', html)
            self.assertNotIn('class="keycap"', html)
        except Exception:
            LOG.exception('An article lacks a working unique illustration')
            raise

    def test_missing_visual_is_blocked_before_publication(self):
        try:
            with tempfile.TemporaryDirectory(prefix='tthq-visual-test-') as folder:
                root = Path(folder)
                (root / 'content').mkdir()
                (root / 'archive').mkdir()
                shutil.copy2(ROOT / 'content/articles.json', root / 'content/articles.json')
                shutil.copy2(ROOT / 'archive/legacy-map.json', root / 'archive/legacy-map.json')
                path = root / 'content/articles.json'
                doc = json.loads(path.read_text())
                doc['articles'][0].pop('visual', None)
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(ValueError, 'needs an approved visual'):
                    read_data(root)
        except Exception:
            LOG.exception('Visual publication gate did not fail closed')
            raise

    def test_duplicate_image_is_blocked(self):
        try:
            with tempfile.TemporaryDirectory(prefix='tthq-visual-test-') as folder:
                root = Path(folder)
                (root / 'content').mkdir()
                (root / 'archive').mkdir()
                shutil.copy2(ROOT / 'content/articles.json', root / 'content/articles.json')
                shutil.copy2(ROOT / 'archive/legacy-map.json', root / 'archive/legacy-map.json')
                path = root / 'content/articles.json'
                doc = json.loads(path.read_text())
                doc['articles'][1]['visual']['src'] = doc['articles'][0]['visual']['src']
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(ValueError, 'unsafe or reused image'):
                    read_data(root)
        except Exception:
            LOG.exception('Duplicate artwork was not rejected')
            raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
