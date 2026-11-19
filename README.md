# Repo Assistant

Repo Assistant liest ein öffentliches Markdown-README, zerlegt es in nachvollziehbare Abschnitte und sucht darin nach Wörtern aus einer Frage. Eine KI-Antwort ist für einen späteren Meilenstein geplant. Für diesen Stand werden weder ein API-Schlüssel noch ein Netzwerkzugriff beim Start gebraucht.

## Voraussetzungen und Start (Windows PowerShell)

Getestet mit Python 3.12. Alle Laufzeitfunktionen verwenden nur die Python-Standardbibliothek.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m repo_assistant.cli
```

Der letzte Befehl liest standardmäßig `data/documents/requests.README.md`. Für eine eigene UTF-8-Datei:

```powershell
.\.venv\Scripts\python.exe -m repo_assistant.cli pfad\zum\README.md
.\.venv\Scripts\python.exe -m repo_assistant.cli pfad\zum\README.md --max-chars 600
```

Jede Ausgabe enthält Abschnittskennung, Überschrift, Originalzeilen und den unveränderten Text. Ein *Chunk* ist hier ein solcher Abschnitt samt Herkunftsangaben. Beispielsweise wird das Kapitel `Installing Requests and Supported Versions` im mitgelieferten README als eigener Chunk angezeigt; der Installationsbefehl bleibt in seinem Codeblock. Längere Kapitel werden zuerst an Leerzeilen, sonst an ganzen Zeilen geteilt. Eine einzelne Zeile über dem Zeichenlimit bleibt vollständig und darf das Limit daher überschreiten. Der Text jeder Originalzeile erscheint genau einmal.

## Fragen suchen

*Retrieval* bedeutet hier, passende Textstellen zu einer Frage zu finden. Die Suche wandelt Großbuchstaben in Kleinbuchstaben um, entfernt Akzente und trennt Satzzeichen. Sie zählt für jeden Chunk die **unterschiedlichen Wörter**, die sowohl in der Frage als auch in Überschrift oder Text vorkommen. Eine Wortwiederholung erhöht die Wertung nicht. Bei gleicher Wertung kommt der frühere Originalabschnitt zuerst. Nur Treffer mit mindestens einem gemeinsamen Wort werden gezeigt, höchstens drei. Die Wertung ist keine Wahrscheinlichkeit für eine richtige Antwort.

```powershell
.\.venv\Scripts\python.exe -m repo_assistant.cli --question "How do I install Requests with pip?"
.\.venv\Scripts\python.exe -m repo_assistant.cli --question "Kann die Bibliothek Verbindungen wiederverwenden?"
```

Die erste Frage findet den Installationsabschnitt auf Rang 1 mit Wertung 3 und einem Link auf `README.md` Zeilen 30–39. Die zweite Frage erhält keine Treffer: Die deutsche Formulierung hat kein gemeinsames Wort mit „Keep-Alive & Connection Pooling“ in Zeile 44. Das zeigt eine Grenze der Wortsuche, obwohl die Dokumentstelle fachlich passt. Ein Treffer kann umgekehrt vorhanden sein, obwohl die gesuchte Antwort im Dokument fehlt.

Für ein eigenes README kann vor `--question` ein Dateipfad angegeben werden. Dann zeigt die Quelle den lokalen Pfad und die Originalzeilen.

## Offline-Auswertung

Die zehn vorab festgelegten Fragen in `data/evaluation/questions.json` gehören zum unten genannten Commit und Datei-Hash. Acht haben überprüfte Belegzeilen; zwei sind als „im Dokument unbeantwortbar“ markiert. Deutsch und Englisch sind vertreten. Die Auswertung prüft die Dateiversion vor der Messung.

```powershell
.\.venv\Scripts\python.exe -m repo_assistant.cli --evaluate
```

*Recall@3* ist der Anteil der beantwortbaren Fragen, deren erwartete Belegzeilen vollständig in einem der ersten drei Treffer liegen. Die gemessene Ausgangsversion erreicht **7/8 = 87,5 %**. Bei Q05 („Kann die Bibliothek Verbindungen wiederverwenden?“) fehlt ein Worttreffer. Die zwei unbeantwortbaren Fragen zählen nicht in Recall@3; die Suche liefert für beide trotzdem Treffer, weil sie nur Wortübereinstimmung misst. Das Programm erzeugt noch keine Antwort und beurteilt daher auch keine Antwortqualität.

## Beispieldokument und Herkunft

Die Kopie unter `data/documents/requests.README.md` stammt aus dem öffentlichen Repository [psf/requests](https://github.com/psf/requests). Originalpfad: `README.md`; Commit: `3c7baaa05ab4aa49cc819ce3a819d260de19c157`. Die [fest gepinnte Quelldatei](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md) und die maschinenlesbaren Angaben in `data/documents/requests.source.json` machen die Version prüfbar. Der lokale Git-Blob-Hash `4e5c44555c02f127cd0cca2efa8b22716c78ee23` stimmt mit der Quelldatei überein. Überschriften, Leerzeilen und Formatierung der Kopie wurden übernommen.

## Prüfung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Die zwölf Tests prüfen weiterhin die Aufteilung aus Meilenstein 1 und zusätzlich Rangfolge, Gleichstand, leere Frage, fehlende Treffer, Dateiversion, den gemessenen Ausgangswert und die Terminalbefehle. Sie benötigen keinen API-Schlüssel.

**Übung zu Meilenstein 1:** Ergänze in einer eigenen README-Kopie vor einem Absatz `## Neue Überschrift` und vergleiche die Abschnittskennungen und Zeilenbereiche.

**Übung zu Meilenstein 2:** Vergleiche `SOCKS Proxy Support` mit `Unterstützt Requests SOCKS-Proxys?` und beobachte, welche gemeinsamen Wörter die Trefferwertung bestimmen.
