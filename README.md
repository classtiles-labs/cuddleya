# cuddleya.de

Öffentliche Seiten der App Cuddleya: Start, Datenschutz, Impressum, Support (Deutsch, Englisch unter `/en`).

Die Inhalte stehen in `_src/<sprache>/<seite>.html`, Kopf und Fuß erzeugt `_build.py`:

```
python3 _build.py
python3 -m unittest discover -s _tests -v
```

Danach die erzeugten HTML-Dateien mit einchecken. Ordner und Dateien mit Unterstrich liefert GitHub
Pages nicht aus (`_src`, `_docs`, `_tests`, `_tools`, `_build.py`).

Keine Cookies, keine fremden Schriften, kein Fremdcode, nur eigenes Skript: `assets/story.js` bewegt die
Startseite und speichert oder sendet nichts. Das sagt die Datenschutzerklärung zu, und dabei soll es bleiben.

Figuren: `assets/figures/` sind Kopien aus `BabyApp/Design/` (im Code gezeichnet, gehören uns), erzeugt mit
`python3 _tools/copy_figures.py`. Das App-Symbol (`assets/icon*.png`, `favicon.png`) stammt aus
`BabyApp/scripts/render_app_icon.py`. Screenshots in `assets/shots/` stammen aus dem Simulator mit einem
erfundenen Beispielkind. Design und Plan: `_docs/`.
