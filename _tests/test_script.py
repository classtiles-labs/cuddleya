import shutil
import subprocess
import unittest

from sitehelp import ROOT, build, page, read

JS = ROOT / "assets" / "story.js"
BANNED = ["fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "indexedDB",
          "document.cookie", "import(", "WebSocket", "http:", "https:", "eval(", "new Function"]
HOOKS = ['class="sky"', 'data-sky="dawn"', 'data-sky="dusk"', 'class="fig-btn"', "data-timer="]


class ScriptTests(unittest.TestCase):
    def test_small(self):
        self.assertLessEqual(JS.stat().st_size, 6144)

    def test_sends_and_stores_nothing(self):
        text = read(JS)
        for bad in BANNED:
            with self.subTest(api=bad):
                self.assertNotIn(bad, text)

    def test_does_what_the_page_needs(self):
        text = read(JS)
        for piece in ['classList.add("js")', '"motion"', "prefers-reduced-motion", "IntersectionObserver",
                      '"--night-o"', '"--glow"', '"--p"', "aria-pressed", "[data-timer]", "requestAnimationFrame"]:
            with self.subTest(piece=piece):
                self.assertIn(piece, text)

    def test_page_offers_every_hook(self):
        build()
        html = read(page("de", "index"))
        for hook in HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(hook, html)

    @unittest.skipUnless(shutil.which("node"), "node fehlt")
    def test_parses(self):
        subprocess.run(["node", "--check", str(JS)], check=True, capture_output=True)
