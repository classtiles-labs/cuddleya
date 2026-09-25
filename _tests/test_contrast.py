import re
import unittest

from sitehelp import ROOT, read


def tokens(block):
    return dict(re.findall(r"--([a-z0-9-]+):(#[0-9a-f]{6})", block))


def luminance(hex_):
    def chan(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (Text, Grund, Mindestwert) — 4.5 für Fließtext, 3 für große oder fette Schrift
PAIRS = [
    ("ink", "day", 4.5), ("ink-2", "day", 4.5), ("ink-3", "day", 4.5), ("ink-2", "tile", 4.5),
    ("ink-3", "tile", 4.5), ("ink-2", "sunk", 4.5), ("navy", "day", 4.5), ("ink", "navy-soft", 4.5),
    ("navy", "navy-soft", 3), ("ink", "rose-soft", 4.5), ("ink-2", "rose-soft", 4.5),
    ("on-night", "night-2", 4.5), ("on-night-2", "night-2", 4.5), ("moon", "night-2", 4.5),
    ("on-night-2", "night", 4.5),
]


class ContrastTests(unittest.TestCase):
    def test_contrast(self):
        css = read(ROOT / "assets" / "site.css")
        light = tokens(css.split("@media (prefers-color-scheme: dark)")[0])
        dark = {**light, **tokens(css.split("@media (prefers-color-scheme: dark)")[1])}
        for mode, t in (("hell", light), ("dunkel", dark)):
            for fg, bg, minimum in PAIRS:
                with self.subTest(mode=mode, pair=f"{fg} auf {bg}"):
                    self.assertGreaterEqual(ratio(t[fg], t[bg]), minimum)
