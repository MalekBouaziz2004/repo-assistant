# Repo Assistant

Repo Assistant zeigt derzeit, wie ein öffentliches Markdown-README in nachvollziehbare Abschnitte zerlegt wird. Die Suche und eine KI-Antwort sind für spätere Meilensteine geplant. Für diesen Stand werden weder ein API-Schlüssel noch ein Netzwerkzugriff beim Start gebraucht.

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

## Beispieldokument und Herkunft

Die Kopie unter `data/documents/requests.README.md` stammt aus dem öffentlichen Repository [psf/requests](https://github.com/psf/requests). Originalpfad: `README.md`; Commit: `3c7baaa05ab4aa49cc819ce3a819d260de19c157`. Die [fest gepinnte Quelldatei](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md) und die maschinenlesbaren Angaben in `data/documents/requests.source.json` machen die Version prüfbar. Der lokale Git-Blob-Hash `4e5c44555c02f127cd0cca2efa8b22716c78ee23` stimmt mit der Quelldatei überein. Überschriften, Leerzeilen und Formatierung der Kopie wurden übernommen.

## Prüfung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Die Tests prüfen eine Einleitung, Überschriften, einen langen Abschnitt, Codeblöcke, unveränderte Originalzeilen und verständliche Fehler für fehlende oder leere Dateien. Sie benötigen keinen API-Schlüssel.

**Übung:** Ergänze in einer eigenen README-Kopie vor einem Absatz `## Neue Überschrift` und vergleiche die Abschnittskennungen und Zeilenbereiche vor und nach der Änderung.
