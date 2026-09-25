import unittest

from sitehelp import ROOT, build, page, parse, read

SHOTS = {"de": ["de-heute", "de-eintrag", "de-figuren"], "en": ["en-today", "en-entry", "en-figures"]}


class ShotTests(unittest.TestCase):
    def test_screenshots_exist_and_are_light(self):
        for names in SHOTS.values():
            for name in names:
                path = ROOT / "assets" / "shots" / f"{name}.jpg"
                with self.subTest(name):
                    self.assertTrue(path.exists())
                    self.assertLess(path.stat().st_size, 250 * 1024)

    def test_pages_show_them_lazily_with_alt_text(self):
        build()
        for lang, names in SHOTS.items():
            root = parse(read(page(lang, "index")))
            imgs = {n.attrs["src"]: n for n in root.walk() if n.tag == "img" and "/shots/" in n.attrs.get("src", "")}
            with self.subTest(lang=lang):
                self.assertEqual(sorted(imgs), sorted(f"/assets/shots/{n}.jpg" for n in names))
                for img in imgs.values():
                    self.assertEqual(img.attrs.get("loading"), "lazy")
                    self.assertGreater(len(img.attrs.get("alt", "")), 20)
