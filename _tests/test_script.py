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

    def test_scene_progress_uses_the_sticky_height(self):
        # innerHeight changes with the iOS toolbar; the sticky part is fixed in svh (review 25.9.)
        text = read(JS)
        self.assertIn("firstElementChild.offsetHeight", text)
        self.assertNotIn("innerHeight", text)

    def test_reveal_observer_says_what_it_does(self):
        text = read(JS)
        self.assertIn("threshold: 0", text)
        self.assertIn("rootMargin", text)

    def test_announces_itself_to_the_early_fallback(self):
        self.assertIn('doc.dataset.story = "1"', read(JS))

    def test_paint_skips_unchanged_values(self):
        self.assertIn("setIfChanged", read(JS))

    def test_page_offers_every_hook(self):
        build()
        html = read(page("de", "index"))
        for hook in HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(hook, html)

    @unittest.skipUnless(shutil.which("node"), "node fehlt")
    def test_parses(self):
        subprocess.run(["node", "--check", str(JS)], check=True, capture_output=True)
