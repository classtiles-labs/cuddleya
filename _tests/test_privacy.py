import unittest

from sitehelp import ROOT, build, page, read


class PrivacyTests(unittest.TestCase):
    def test_privacy_pages_mention_the_own_script(self):
        build()
        self.assertIn("eigenes Skript", read(page("de", "datenschutz")))
        self.assertIn("script of our own", read(page("en", "privacy")))

    def test_readme_matches_the_site(self):
        text = read(ROOT / "README.md")
        self.assertIn("nur eigenes Skript", text)
        self.assertIn("_tools/copy_figures.py", text)
        self.assertNotIn("Keine Cookies, keine Skripte", text)
