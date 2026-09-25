#!/usr/bin/env python3
"""Baut die statischen Seiten von cuddleya.de aus Rahmen + Inhaltsdateien.

Inhalte liegen in _src/<lang>/<name>.html, der Rahmen (Kopf, Navigation, Fuß) entsteht hier.
Die Startseite bekommt zusätzlich story.css und story.js (eigenes Skript, kein Fremdcode).
Ausgabe ins Repo-Verzeichnis. Ordner und Dateien mit Unterstrich liefert GitHub Pages (Jekyll) nicht aus.
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "_src"
OUT = ROOT
BASE = "https://cuddleya.de"

# (Datei de, Datei en, Titel de, Titel en, Beschreibung de, Beschreibung en)
PAGES = [
    ("index", "index", "Cuddleya", "Cuddleya",
     "Cuddleya ist ein ruhiges Babytagebuch für iPhone und Apple Watch: Schlaf, Mahlzeiten und Windeln festhalten, den Tag auf einer Achse sehen, gemeinsam mit dem Partner.",
     "Cuddleya is a calm baby log for iPhone and Apple Watch: record sleep, feeds and diapers, see the day on one axis, together with your partner."),
    ("datenschutz", "privacy", "Datenschutz", "Privacy Policy",
     "Datenschutzerklärung der App Cuddleya und dieser Website.",
     "Privacy policy of the Cuddleya app and this website."),
    ("impressum", "imprint", "Impressum", "Imprint",
     "Impressum der App Cuddleya.", "Legal notice of the Cuddleya app."),
    ("support", "support", "Support", "Support",
     "Hilfe und Kontakt zur App Cuddleya.", "Help and contact for the Cuddleya app."),
]

NAV = {
    "de": [("index", "Start"), ("datenschutz", "Datenschutz"), ("impressum", "Impressum"), ("support", "Support")],
    "en": [("index", "Home"), ("privacy", "Privacy"), ("imprint", "Imprint"), ("support", "Support")],
}
SKIP = {"de": "Zum Inhalt", "en": "Skip to content"}
STORY = ('\n  <link rel="stylesheet" href="/assets/story.css">'
         '\n  <script src="/assets/story.js" defer></script>')
# Setzt .js/.motion vor dem ersten Zeichnen, damit Szenen und Einblendungen nicht nachträglich springen.
EARLY = ('\n  <script>(d=>{d.classList.add("js");'
         'if(!matchMedia("(prefers-reduced-motion: reduce)").matches){d.classList.add("motion");'
         'setTimeout(()=>d.dataset.story||d.classList.remove("motion"),4000)}})'
         '(document.documentElement)</script>')


def url(lang, name):
    prefix = "/en/" if lang == "en" else "/"
    return prefix if name == "index" else f"{prefix}{name}.html"


def render(lang, name, other_name, title, desc, body):
    other = "en" if lang == "de" else "de"
    home = name == "index"
    de_url = url("de", name if lang == "de" else other_name)
    en_url = url("en", name if lang == "en" else other_name)
    full_title = html.escape("Cuddleya" if home else f"{title} — Cuddleya")
    desc = html.escape(desc)
    current = ' aria-current="page"'
    nav = "".join(
        f'<a href="{url(lang, n)}"{current if n == name else ""}>{label}</a>'
        for n, label in NAV[lang]
    )
    switch_label = "English" if lang == "de" else "Deutsch"
    switch_href = en_url if lang == "de" else de_url
    footer = "".join(f'<a href="{url(lang, n)}">{label}</a>' for n, label in NAV[lang][1:])
    content = body.strip()
    main = (f'<main id="inhalt">\n{content}\n</main>' if home
            else f'<main id="inhalt"><div class="wrap">\n{content}\n</div></main>')
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">{EARLY if home else ""}
  <title>{full_title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#0f1016">
  <link rel="canonical" href="{BASE}{url(lang, name)}">
  <link rel="alternate" hreflang="de" href="{BASE}{de_url}">
  <link rel="alternate" hreflang="en" href="{BASE}{en_url}">
  <link rel="alternate" hreflang="x-default" href="{BASE}{de_url}">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{BASE}/assets/icon.png">
  <link rel="icon" type="image/png" href="/assets/favicon.png">
  <link rel="apple-touch-icon" href="/assets/icon.png">
  <link rel="stylesheet" href="/assets/site.css">{STORY if home else ""}
</head>
<body class="{"home" if home else "doc"}">
<a class="skip" href="#inhalt">{SKIP[lang]}</a>
<header class="site"><div class="wrap">
  <a class="brand" href="{url(lang, 'index')}"><img src="/assets/icon-96.png" alt="" width="36" height="36">Cuddleya</a>
  <nav class="tabs">{nav}<a href="{switch_href}" hreflang="{other}" rel="alternate">{switch_label}</a></nav>
</div></header>
{main}
<footer class="site"><div class="wrap">
  <span>© 2026 Stefan Venekamp</span>{footer}
</div></footer>
</body>
</html>
"""


def main():
    for de, en, t_de, t_en, d_de, d_en in PAGES:
        for lang, name, other, title, desc in (("de", de, en, t_de, d_de), ("en", en, de, t_en, d_en)):
            body = (SRC / lang / f"{name}.html").read_text(encoding="utf-8")
            target = OUT / ("en" if lang == "en" else "") / f"{name}.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(lang, name, other, title, desc, body), encoding="utf-8")
            print("wrote", target.relative_to(OUT))


if __name__ == "__main__":
    main()
