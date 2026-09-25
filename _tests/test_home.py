import re
import unittest

from sitehelp import ANIMALS, ROOT, build, by_id, local_target, page, parse, read, visible_text

LANGS = ["de"]  # Task 5 ergänzt "en"
SECTIONS = ["s-night", "s-dawn", "s-log", "s-day", "s-forecast", "s-devices",
            "s-together", "s-figures", "s-dusk", "s-data", "s-end"]
FORBIDDEN = {
    "de": r"besser schlaf|mehr schlaf|durchschlaf|\bgenau|präzis|zuverlässig|garantie|\bKI\b|künstliche intelligenz|intelligent|wissenschaftlich|klinisch|empfohlen von|nie wieder|\d\s?%",
    "en": r"sleep better|more sleep|sleep through|accura|precis|reliab|guarantee|\bAI\b|artificial intelligence|\bsmart|intelligen|scientific|clinical|recommended by|never again|\d\s?%",
}
SECRETS = (ROOT / ".secret-words").read_text().strip() if (ROOT / ".secret-words").exists() else r"(?!)"
REQUIRED = {
    "de": ["Orientierung, kein Plan", "etwa acht Wochen", "ersetzt keine ärztliche Beratung",
           "kein Medizinprodukt", "Bald im App Store"],
    "en": ["Guidance, not a plan", "about eight weeks", "does not replace medical advice",
           "not a medical device", "Coming soon to the App Store"],
}
TAG = {"de": "Beispiel", "en": "Example"}
NAME = {"de": 1, "en": 2}
# Zustände, die auch ohne .motion unsichtbar sein dürfen: die zweite Hälfte eines Figurenwechsels
STATIC_HIDDEN = ("#s-dawn .asleep", "#s-dusk .awake", ".fig-btn .asleep")


def images(root):
    return [n for n in root.walk() if n.tag == "img"]


class HomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.html = {lang: read(page(lang, "index")) for lang in LANGS}
        cls.docs = {lang: parse(text) for lang, text in cls.html.items()}

    def test_sections_in_story_order(self):
        for lang, root in self.docs.items():
            ids = [n.attrs["id"] for n in root.walk() if n.attrs.get("id", "").startswith("s-")]
            self.assertEqual(ids, SECTIONS, lang)

    def test_required_phrases(self):
        for lang, root in self.docs.items():
            text = visible_text(root)
            for phrase in REQUIRED[lang]:
                with self.subTest(lang=lang, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_no_promises(self):
        for lang, root in self.docs.items():
            text = visible_text(root)
            with self.subTest(lang=lang):
                self.assertIsNone(re.search(FORBIDDEN[lang], text, re.I), re.search(FORBIDDEN[lang], text, re.I))
                self.assertNotRegex(text, r"\bWHO\b")

    def test_forecast_keeps_its_secrets(self):
        for lang, root in self.docs.items():
            text = visible_text(by_id(root, "s-forecast"))
            with self.subTest(lang=lang):
                self.assertIsNone(re.search(SECRETS, text, re.I), re.search(SECRETS, text, re.I))

    def test_every_example_is_labelled(self):
        for lang, root in self.docs.items():
            examples = [n for n in root.walk() if "example" in n.classes()]
            self.assertGreaterEqual(len(examples), 4)
            for node in examples:
                tags = [c for c in node.walk() if "example-tag" in c.classes()]
                with self.subTest(lang=lang, example=node.attrs.get("class")):
                    self.assertEqual(len(tags), 1)
                    self.assertEqual(tags[0].text_content().strip(), TAG[lang])

    def test_images_graphics_and_buttons_are_accessible(self):
        for lang, root in self.docs.items():
            for node in root.walk():
                hidden = any(a.attrs.get("aria-hidden") == "true" for a in node.ancestors())
                with self.subTest(lang=lang, tag=node.tag, cls=node.attrs.get("class")):
                    if node.tag == "img":
                        self.assertIn("alt", node.attrs)
                    if node.tag == "svg" and not hidden:
                        labelled = node.attrs.get("role") == "img" and node.attrs.get("aria-label")
                        self.assertTrue(node.attrs.get("aria-hidden") == "true" or labelled)
                    if node.tag == "button":
                        self.assertTrue(node.text_content().strip() or node.attrs.get("aria-label"))

    def test_all_fifteen_figures_can_be_tapped(self):
        for lang, root in self.docs.items():
            buttons = [n for n in root.walk() if "fig-btn" in n.classes()]
            names = [" ".join(b.text_content().split()) for b in buttons]
            self.assertEqual(names, [a[NAME[lang]] for a in ANIMALS], lang)
            for b in buttons:
                self.assertEqual(b.attrs.get("type"), "button")
                self.assertEqual(b.attrs.get("aria-pressed"), "false")

    def test_page_weight(self):
        for lang, root in self.docs.items():
            eager = {n.attrs["src"] for n in images(root) if n.attrs.get("loading") != "lazy"}
            lazy = {n.attrs["src"] for n in images(root)
                    if n.attrs.get("loading") == "lazy" and not n.attrs["src"].startswith("/assets/shots/")}
            files = ["/assets/site.css", "/assets/story.css", "/assets/story.js", *eager]
            first = len(self.html[lang].encode()) + sum(local_target(f).stat().st_size for f in files)
            later = sum(local_target(f).stat().st_size for f in lazy)
            with self.subTest(lang=lang, first=first, later=later):
                self.assertLess(first, 150 * 1024)
                self.assertLess(later, 110 * 1024)

    def test_hidden_states_need_motion(self):
        css = re.sub(r"/\*.*?\*/", "", read(ROOT / "assets" / "story.css"), flags=re.S)
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            if re.search(r"opacity:\s*0(?![.\d])", body):
                for sel in selectors.split(","):
                    sel = sel.strip()
                    with self.subTest(selector=sel):
                        self.assertTrue(sel.startswith(".motion") or sel.startswith(STATIC_HIDDEN) or "@" in sel)
