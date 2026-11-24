# Repo Assistant

Repo Assistant liest ein öffentliches Markdown-README, zerlegt es in nachvollziehbare Abschnitte und sucht darin nach Wörtern aus einer Frage. Zusätzlich kann Groq aus den gefundenen Passagen eine deutschsprachige Antwort erzeugen. Die Befehle zum Anzeigen, Suchen und Offline-Auswerten funktionieren weiterhin ohne API-Schlüssel und Netzwerkzugriff.

## Voraussetzungen und Start (Windows PowerShell)

Getestet mit Python 3.12. Die Anwendung verwendet nur die Python-Standardbibliothek; für den KI-Befehl wird eine HTTPS-Anfrage an Groq gesendet.

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

*Recall@3* ist der Anteil der beantwortbaren Fragen, deren erwartete Belegzeilen vollständig in einem der ersten drei Treffer liegen. Die gemessene Ausgangsversion erreicht **7/8 = 87,5 %**. Bei Q05 („Kann die Bibliothek Verbindungen wiederverwenden?“) fehlt ein Worttreffer. Die zwei unbeantwortbaren Fragen zählen nicht in Recall@3; die Suche liefert für beide trotzdem Treffer, weil sie nur Wortübereinstimmung misst. Diese Kennzahl beurteilt keine Antwortqualität.

## KI-Antwort mit Groq

*RAG* (Retrieval-Augmented Generation) verbindet die lokale Suche mit einer Antwort aus den gefundenen Textstellen. Beispiel: Bei „How do I install Requests with pip?“ findet die Suche unter anderem Zeilen 30–39. Das Modell bekommt die Frage und bis zu drei ausgewählte Passagen, jeweils mit einer kurzen Kennung wie `S1`, Überschrift und Originalzeilen. Ein *Prompt* ist diese Eingabe zusammen mit der Anweisung, ausschließlich aus den Passagen auf Deutsch zu antworten. Dokumenttext wird als Daten behandelt; Anweisungen in ihm sollen nicht befolgt werden.

Das Modell liefert ein JSON-Objekt mit `answerable`, `answer` und `sources`. Die Anwendung prüft, ob die genannten Kennungen wirklich zu übergebenen Passagen gehören, und bildet Links selbst aus dem gespeicherten Commit und den Originalzeilen. Fehlt eine Kennung oder ist sie unbekannt, zeigt sie stattdessen eine Fehlermeldung und die gefundenen Passagen. **Diese technische Prüfung bestätigt nur die Quellenzuordnung.** Ob eine Aussage inhaltlich durch die Passage gedeckt ist, muss zusätzlich anhand der Referenzfragen und menschlich geprüft werden.

Bei keiner Wortübereinstimmung wird Groq nicht aufgerufen. Bei Worttreffern ohne Antwort, etwa der Lizenzfrage Q10, soll das Modell ausdrücklich „im bereitgestellten Dokument nicht beantwortbar“ sagen. Die Suche allein kann diesen Fall nicht erkennen.

### Modell und kostenloser Zugang

Stand **24. November 2026**: Der Anbieter ist **Groq**, der gewählte Startwert für `GROQ_MODEL` ist **`openai/gpt-oss-20b`**. [Groq führt das Modell im Free-Plan mit begrenzten Kontingenten](https://console.groq.com/docs/rate-limits) und in seiner [Modellübersicht](https://console.groq.com/docs/models). [OpenAI beschreibt die Modellgewichte als Apache-2.0-lizenziert](https://openai.com/open-models/). Offene Gewichte und kostenlose API-Nutzung sind verschiedene Eigenschaften; die Free-Kontingente können sich ändern. Die früher genannten Llama-Modelle sind laut [Groqs Deprecation-Liste](https://console.groq.com/docs/deprecations) für Free-Konten seit August 2026 abgeschaltet. Die Verfügbarkeit im **eigenen Konto** ist noch nicht geprüft. Prüfe vor dem ersten Aufruf in Groq die Konto-Stufe „Free“, die Modellberechtigung und die aktuellen Limits; ein Wechsel zu einem bezahlten Tarif ist nicht vorgesehen.

`.env.example` enthält absichtlich leere Werte. Die Anwendung liest echte Werte aus Umgebungsvariablen; sie lädt keine `.env`-Datei. `.env` ist durch Git ignoriert. Der zusätzliche Wert `GROQ_FREE_TIER_CONFIRMED=1` ist eine bewusste Bestätigung nach der Prüfung des eigenen Kontos. Er kann den tatsächlichen Abrechnungsstatus technisch nicht nachweisen.

Für PowerShell kann der Schlüssel ohne sichtbare Eingabe für die aktuelle Sitzung gesetzt werden:

```powershell
$secureKey = Read-Host "Groq API key" -AsSecureString
$keyPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try { $env:GROQ_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPtr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPtr) }
$env:GROQ_MODEL = "openai/gpt-oss-20b"
$env:GROQ_FREE_TIER_CONFIRMED = "1"
```

Danach ist der KI-Befehl bewusst einzeln ausführbar:

```powershell
.\.venv\Scripts\python.exe -m repo_assistant.cli --answer "How do I install Requests with pip?"
```

Der separate Live-Smoke-Test verwendet Q01 und höchstens **einen** Generierungsaufruf:

```powershell
.\.venv\Scripts\python.exe -m repo_assistant.cli --live-test
```

Er prüft technisch die Antwortstruktur und Quellenkennungen. Vergleiche die Aussage anschließend selbst mit [Zeilen 30–39](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L30-L39). Frage und ausgewählte öffentliche Passagen werden an Groq übertragen. Pro Frage gibt es höchstens einen API-Aufruf ohne automatische Wiederholung; das Kontextbudget beträgt 12.000 Zeichen, die Frage höchstens 1.000 Zeichen, die Antwort höchstens 500 Completion-Tokens und die Wartezeit 30 Sekunden. Zeichen und Tokens sind unterschiedliche Größen; die Eignung dieser Startwerte muss live geprüft werden. Bei Rate-Limit, Modell-, Schlüssel-, Netzwerk- oder Zeitfehler bleiben die lokalen Treffer sichtbar.

### Verifizierte Fälle und offene Prüfung

Offline mit simuliertem Client: Q01 lieferte die korrekte Installationsanweisung mit `S1` und einem Link auf Zeilen 30–39. Q05 hatte keine Treffer und keinen Client-Aufruf. Q10 hatte Worttreffer; die simulierte Antwort sagte korrekt, dass die Lizenz im README nicht genannt ist. Ein erfundenes `S9` wurde abgewiesen, und die gefundenen Passagen blieben sichtbar. Die echte Antwortqualität für diese und die übrigen Referenzfragen ist **noch nicht live geprüft**. Hier waren weder Zugangsdaten noch eine Bestätigung des Free-Tarifs vorhanden; der Live-Test blieb ausstehend.

## Beispieldokument und Herkunft

Die Kopie unter `data/documents/requests.README.md` stammt aus dem öffentlichen Repository [psf/requests](https://github.com/psf/requests). Originalpfad: `README.md`; Commit: `3c7baaa05ab4aa49cc819ce3a819d260de19c157`. Die [fest gepinnte Quelldatei](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md) und die maschinenlesbaren Angaben in `data/documents/requests.source.json` machen die Version prüfbar. Der lokale Git-Blob-Hash `4e5c44555c02f127cd0cca2efa8b22716c78ee23` stimmt mit der Quelldatei überein. Überschriften, Leerzeilen und Formatierung der Kopie wurden übernommen.

## Prüfung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Die 23 Offline-Tests prüfen weiterhin M1 und M2 und zusätzlich Kontextgrenze, Prompt, Quellenkennungen, die drei Referenzfälle sowie simulierte API-Fehler. Sie benötigen keinen API-Schlüssel und führen keinen Anbieteraufruf aus.

**Übung zu Meilenstein 1:** Ergänze in einer eigenen README-Kopie vor einem Absatz `## Neue Überschrift` und vergleiche die Abschnittskennungen und Zeilenbereiche.

**Übung zu Meilenstein 2:** Vergleiche `SOCKS Proxy Support` mit `Unterstützt Requests SOCKS-Proxys?` und beobachte, welche gemeinsamen Wörter die Trefferwertung bestimmen.

**Übung zu Meilenstein 3:** Vergleiche in den Offline-Tests die simulierte Antwort mit `S1` mit einer Antwort, die `S9` nennt. Beobachte, warum die zweite Antwort verworfen wird, obwohl ihr Text plausibel klingen könnte.
