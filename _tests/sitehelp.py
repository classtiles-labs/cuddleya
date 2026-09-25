"""Hilfen für die Seitentests: bauen, lesen, ein kleiner DOM ohne Abhängigkeiten."""
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = {
    "de": ["index", "datenschutz", "impressum", "support"],
    "en": ["index", "privacy", "imprint", "support"],
}
# (Datei, de, en) — Namen aus BabyUI/Resources/Localizable.xcstrings (companion.*), Reihenfolge wie Companion.swift
ANIMALS = [
    ("bear", "Bär", "Bear"), ("bunny", "Häschen", "Bunny"), ("fox", "Fuchs", "Fox"),
    ("cat", "Katze", "Cat"), ("puppy", "Welpe", "Puppy"), ("piglet", "Schweinchen", "Piglet"),
    ("mouse", "Maus", "Mouse"), ("lamb", "Schaf", "Lamb"), ("panda", "Panda", "Panda"),
    ("koala", "Koala", "Koala"), ("raccoon", "Waschbär", "Raccoon"), ("hedgehog", "Igel", "Hedgehog"),
    ("lion", "Löwe", "Lion"), ("elephant", "Elefant", "Elephant"), ("dino", "Dino", "Dino"),
]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
_built = False


def build():
    global _built
    if not _built:
        subprocess.run([sys.executable, str(ROOT / "_build.py")], check=True, capture_output=True)
        _built = True


def page(lang, name):
    return ROOT / ("en" if lang == "en" else "") / f"{name}.html"


def all_pages():
    for lang, names in PAGES.items():
        for name in names:
            yield lang, name, page(lang, name)


def read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def local_target(url):
    path = url.split("#")[0].split("?")[0]
    if path.endswith("/"):
        path += "index.html"
    return ROOT / path.lstrip("/")


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def text_content(self):
        return "".join(c if isinstance(c, str) else c.text_content() for c in self.children)


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse(text):
    parser = _Parser()
    parser.feed(text)
    parser.close()
    return parser.root


def by_id(root, id_):
    return next((n for n in root.walk() if n.attrs.get("id") == id_), None)


def visible_text(node):
    extra = [n.attrs[k] for n in node.walk() for k in ("alt", "aria-label") if n.attrs.get(k)]
    return re.sub(r"\s+", " ", " ".join([node.text_content(), *extra]))
