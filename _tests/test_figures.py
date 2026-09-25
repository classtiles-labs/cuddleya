import subprocess
import sys
import unittest

from sitehelp import ANIMALS, ROOT, read

FIG = ROOT / "assets" / "figures"
SOURCE = ROOT.parent / "BabyApp" / "Design"
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 150">'


class FigureTests(unittest.TestCase):
    def test_every_companion_has_awake_and_asleep(self):
        expected = {f"{a}-{s}.svg" for a, _, _ in ANIMALS for s in ("awake", "asleep")}
        expected.add("bear-asleep-night.svg")
        self.assertEqual({p.name for p in FIG.glob("*.svg")}, expected)

    def test_figures_are_clean_copies(self):
        for path in FIG.glob("*.svg"):
            with self.subTest(path.name):
                text = read(path)
                self.assertTrue(text.startswith(HEAD))
                self.assertNotIn('<rect width="240" height="150"', text)
                self.assertNotIn("<!--", text)

    def test_night_bear_uses_the_dark_cloud(self):
        text = read(FIG / "bear-asleep-night.svg")
        self.assertIn("#282a35", text)
        self.assertIn("#20222c", text)
        self.assertNotIn("#f4f1f6", text)

    @unittest.skipUnless(SOURCE.exists(), "BabyApp/Design fehlt")
    def test_copy_is_repeatable(self):
        before = {p.name: read(p) for p in FIG.glob("*.svg")}
        subprocess.run([sys.executable, str(ROOT / "_tools" / "copy_figures.py")], check=True, capture_output=True)
        self.assertEqual({p.name: read(p) for p in FIG.glob("*.svg")}, before)
