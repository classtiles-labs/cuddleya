#!/usr/bin/env python3
"""Kopiert die Schlaffiguren aus BabyApp/Design nach assets/figures.

Die Vorlagen sind im Code gezeichnet (BabyUI/Illustration, CompanionScene.swift) und gehören uns.
Entfernt wird nur der Hintergrund (die Seite liefert ihn), dazu Kommentare und Leerraum.
bear-asleep-night.svg bekommt die dunkle Wolke der App (hair über sunk) für die Nachtszenen.
Aufruf: python3 _tools/copy_figures.py [Pfad/zu/BabyApp/Design]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "figures"
ANIMALS = ["bear", "bunny", "fox", "cat", "puppy", "piglet", "mouse", "lamb",
           "panda", "koala", "raccoon", "hedgehog", "lion", "elephant", "dino"]
HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 150">'
CLOUD_DAY = ("#f4f1f6", "#e3dde9")
CLOUD_NIGHT = ("#282a35", "#20222c")


def clean(text):
    text, found = re.subn(r'\s*<rect width="240" height="150"[^>]*/>', "", text, count=1)
    if found != 1:
        raise ValueError("Vorlage ohne Hintergrund-Rechteck: Form geändert, bitte prüfen")
    text, heads = re.subn(r"<svg[^>]*>", HEAD, text, count=1)
    if heads != 1:
        raise ValueError("Vorlage ohne <svg>-Kopf")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r">\s+<", "><", text)
    return text.strip() + "\n"


def night(text):
    for day, dark in zip(CLOUD_DAY, CLOUD_NIGHT):
        if day not in text:
            raise ValueError(f"Wolkenfarbe {day} fehlt: Vorlage geändert, bitte prüfen")
        text = text.replace(day, dark)
    return text


def main():
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "BabyApp" / "Design"
    OUT.mkdir(parents=True, exist_ok=True)
    for animal in ANIMALS:
        for state in ("awake", "asleep"):
            name = f"{animal}-{state}.svg"
            (OUT / name).write_text(clean((src / name).read_text(encoding="utf-8")), encoding="utf-8")
    bear = (OUT / "bear-asleep.svg").read_text(encoding="utf-8")
    (OUT / "bear-asleep-night.svg").write_text(night(bear), encoding="utf-8")
    expected = {f"{a}-{s}.svg" for a in ANIMALS for s in ("awake", "asleep")} | {"bear-asleep-night.svg"}
    found = {p.name for p in OUT.glob("*.svg")}
    if found != expected:
        raise SystemExit(f"unerwartete Dateien in {OUT}: {sorted(found ^ expected)}")
    print("wrote", len(found), "figures")


if __name__ == "__main__":
    main()
