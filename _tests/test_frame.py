import re
import struct
import unittest

from sitehelp import ROOT, all_pages, build, local_target, read

EXTERNAL = re.compile(r'(?:src|href)="(?:https?:)?//(?!cuddleya\.de(?:/|"))')
REF = re.compile(r'(?:src|href)="(/[^"]*)"')


class FrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()

    def test_every_page_has_language_skip_link_and_main(self):
        for lang, _, path in all_pages():
            with self.subTest(page=str(path.relative_to(ROOT))):
                html = read(path)
                self.assertTrue(html.startswith("<!doctype html>"))
                self.assertIn(f'<html lang="{lang}">', html)
                self.assertIn('<a class="skip" href="#inhalt">', html)
                self.assertIn('<main id="inhalt">', html)
                self.assertIn('<meta name="theme-color" content="#0f1016">', html)

    def test_story_assets_only_on_home(self):
        for _, name, path in all_pages():
            html = read(path)
            with self.subTest(page=str(path.relative_to(ROOT))):
                if name == "index":
                    self.assertIn('<script src="/assets/story.js" defer></script>', html)
                    self.assertIn('<link rel="stylesheet" href="/assets/story.css">', html)
                    self.assertIn('<body class="home">', html)
                else:
                    self.assertNotIn("story.", html)
                    self.assertIn('<body class="doc">', html)

    def test_no_third_party_resources(self):
        for _, _, path in all_pages():
            html = read(path)
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertIsNone(EXTERNAL.search(html))
                for tag in re.findall(r"<script[^>]*>", html):
                    self.assertEqual(tag, '<script src="/assets/story.js" defer>')
        for css in (ROOT / "assets").glob("*.css"):
            self.assertNotRegex(read(css), r"@import|url\(\s*['\"]?(?:https?:)?//")

    def test_local_references_exist(self):
        for _, _, path in all_pages():
            for ref in REF.findall(read(path)):
                with self.subTest(page=str(path.relative_to(ROOT)), ref=ref):
                    self.assertTrue(local_target(ref).exists())


def png_size(path):
    return struct.unpack(">II", path.read_bytes()[16:24])


class IconTests(unittest.TestCase):
    """Neues App-Symbol (Häschen im Mond, BabyApp PR #73) in drei Größen."""

    def test_icon_sizes(self):
        assets = ROOT / "assets"
        self.assertEqual(png_size(assets / "icon.png"), (512, 512))
        self.assertEqual(png_size(assets / "icon-96.png"), (96, 96))
        self.assertEqual(png_size(assets / "favicon.png"), (64, 64))

    def test_header_uses_the_small_icon(self):
        build()
        for _, _, path in all_pages():
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertIn('<img src="/assets/icon-96.png" alt="" width="36" height="36">', read(path))
