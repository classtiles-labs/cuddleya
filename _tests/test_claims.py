"""Korrekturen aus der Belegprüfung gegen BabyApp origin/main ce3c6a08 (25.9.)."""
import unittest

from sitehelp import build, page, parse, read, visible_text

GONE = {
    "de": ["Einschlafdauer", "über das Teilen-Blatt oder einen QR-Code", "bei jedem Eintrag, wer ihn gemacht hat",
           "Alle Einträge mit Suche und Filtern", "Wer nicht teilen will", "Schläft seit 1:12:05"],
    "en": ["time to fall asleep", "via the share sheet or a QR code", "each entry shows who added it",
           "Every entry with search and filters", "If you don’t want to share", "likely bedtime",
           "Sleeping since 1:12:05"],
}
THERE = {
    "de": ["jeden Monat bis zum ersten Geburtstag", "Suche in den Notizen", "Apples iCloud-Freigabe",
           "Bei Einträgen der anderen Person steht ihr Name", "Ohne iCloud geht es auch",
           "Orientierung aus Mias letzten 42 Schlafphasen", "Schläfchen, 24 Std.", "Spruch des Tages"],
    "en": ["every month until the first birthday", "note search", "Apple’s iCloud sharing",
           "Entries made by the other person show their name", "Without iCloud it works too",
           "Guidance from Mia’s last 42 sleeps", "Naps, 24 h", "Daily quote"],
}


class ClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build()
        cls.text = {lang: visible_text(parse(read(page(lang, "index")))) for lang in ("de", "en")}

    def test_overstatements_are_gone(self):
        for lang, phrases in GONE.items():
            for phrase in phrases:
                with self.subTest(lang=lang, phrase=phrase):
                    self.assertNotIn(phrase, self.text[lang])

    def test_corrected_wording_is_there(self):
        for lang, phrases in THERE.items():
            for phrase in phrases:
                with self.subTest(lang=lang, phrase=phrase):
                    self.assertIn(phrase, self.text[lang])
