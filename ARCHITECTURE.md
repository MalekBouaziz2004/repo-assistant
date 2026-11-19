# Architektur

## Zweck und Status

Dieses Dokument beschreibt den Zielaufbau. Meilenstein 1 ist implementiert: Ein lokales README wird über die Terminaloberfläche eingelesen und in Abschnitte mit Originalzeilen zerlegt. Suche und Generierung sind weiterhin geplant.

Repo Assistant verwendet Dokumentation als Wissensquelle. Der erste Einstieg ist ein Python-Programm im Terminal. Die Dokumentsuche läuft lokal, die spätere Textgenerierung bei Groq im kostenlosen Tarif. Die Architektur benötigt für den ersten Ablauf einen Python-Prozess und Textdateien.

## Entscheidungen

| Bereich | Vorgesehene Lösung | Grund |
| --- | --- | --- |
| Sprache | Python | Lesbarer Einstieg und direkter Zugang zu KI-Werkzeugen |
| Bedienung | Terminal | Sichtbare Zwischenergebnisse beim Lernen |
| Quelldaten | Zunächst ein lokales öffentliches README mit Herkunftsdaten | Reproduzierbare Versuche |
| Zerlegung | Markdown-Abschnitte mit Zeilenangaben und Größenbegrenzung | Nachvollziehbare Quellen und begrenzter Kontext |
| Suche | Zunächst Wortübereinstimmungen | Einfach messbare Ausgangsversion |
| Generierung | Groq-Free-Tarif, Modell per Konfiguration | Gehostete Verarbeitung bei einem Budget von 0 Euro |
| Speicherung | UTF-8-Dateien und JSON-Metadaten | Ausreichend für wenige Dokumente |
| Verifikation | Kleine Offline-Tests mit `unittest`; feste Referenzfragen ab Meilenstein 2 | Wiederholbare Prüfungen ohne API-Verbrauch |

Die kostenlose Verfügbarkeit und die Lizenz des gewählten Modells werden bei seiner Auswahl dokumentiert. Groq ist eine technische Ausgangsentscheidung. Ein Anbieterwechsel soll die Dokumentverarbeitung und Referenzfragen weiterverwenden können.

## Datenfluss

Beim Import liest das Programm ein Dokument und speichert seine Herkunft. Es zerlegt den Inhalt in Abschnitte, die zum Original zurückführen.

Bei einer Frage bewertet die Suche diese Abschnitte und gibt bis zu drei passende Treffer zurück. Schon diese Treffer bilden eine nutzbare Ausgabe. Für die RAG-Version wird aus Frage und Treffern ein Prompt erstellt. Ein Prompt besteht hier aus Arbeitsanweisung und Eingaben für das Sprachmodell.

Der API-Client überträgt diesen Prompt und empfängt die Antwort. Anschließend prüft die Anwendung die Quellenkennungen und zeigt Antwort und Quellen an. Wenn kein Treffer vorliegt, meldet sie fehlende Belege ohne API-Aufruf. Ein Suchtreffer kann thematisch ähnlich sein und trotzdem die Frage offenlassen. Deshalb wird auch dieser Fall in der Antwortbewertung geprüft.

## Geplante Dateien

Die Einträge werden mit dem jeweils passenden Meilenstein angelegt.

| Pfad | Aufgabe |
| --- | --- |
| src/repo_assistant/cli.py | Argumente, Terminalausgabe und Ablaufsteuerung |
| src/repo_assistant/documents.py | Einlesen, Markdown-Aufteilung und Quelldaten |
| src/repo_assistant/retrieval.py | Bewertung und Auswahl der Treffer |
| src/repo_assistant/generation.py | Prompt und Groq-Aufruf |
| src/repo_assistant/evaluation.py | Referenzfragen ausführen und Ergebnisse auswerten |
| data/documents/ | Ausgewählte öffentliche Beispieldokumente samt Herkunft |
| data/evaluation/questions.json | Fragen mit erwarteten Belegen |
| tests/ | Kleine deterministische Prüfungen |
| .env.example | Konfigurationsnamen mit leeren Beispielwerten |
| pyproject.toml | Python-Paket und benötigte Abhängigkeiten |

Für Meilenstein 1 genügen Dokumentverarbeitung, CLI und zugehörige Prüfungen. Eine einfache Funktion pro fachlicher Aufgabe reicht zunächst aus. Ausführbare Befehle werden erst zusammen mit ihrer Implementierung im README dokumentiert.

## Daten und Quellen

Ein Dokument erhält eine stabile Kennung, Repository-URL, Pfad, Commit und Originaltext. Bei einem GitHub-Import wird zuerst der aktuelle Commit ermittelt und anschließend die Datei genau aus dieser Version geladen. Diese Version steht auch im Quellenlink.

Ein Abschnitt speichert Dokumentkennung, Abschnittskennung, Überschrift, erste und letzte Originalzeile sowie Text. Lange Abschnitte werden geteilt und behalten die Originalzeilen ihrer Teile. Ein Treffer ergänzt den Suchwert und die Rangposition.

Für den Modellaufruf bekommen die ausgewählten Treffer kurze Kennungen wie S1 und S2. Die Anwendung verwaltet die Zuordnung zu den Originalquellen. Sie bildet Links selbst aus gespeicherten Quelldaten, beispielsweise mit einem Commit und einem GitHub-Zeilenfragment.

Die Quellenprüfung stellt fest, ob eine angeführte Kennung tatsächlich übergeben wurde. Ob die Passage die Aussage inhaltlich stützt, wird mit den Referenzfragen und einer menschlichen Prüfung bewertet.

## Konfiguration und API-Verbrauch

GROQ_API_KEY und GROQ_MODEL werden aus der Umgebung geladen. Die spätere .env.example enthält ausschließlich Platzhalter. Eine lokale .env-Datei wird durch Git ignoriert.

Für den ersten Stand gelten ein maximaler Kontext von 12.000 Zeichen, ein Antwortlimit von etwa 500 Tokens und eine Wartezeit von 30 Sekunden als Startwerte. Das genaue SDK-Feld für die Antwortbegrenzung wird anhand der aktuellen API geprüft. Kontextbudget und Modelllimit werden berücksichtigt. Zeichen und Tokens sind verschiedene Größen, deshalb dokumentiert der Live-Test die Eignung dieser Startwerte.

Eine Frage löst höchstens einen Generierungsaufruf aus. Automatische Wiederholungen und Anbieterwechsel bleiben deaktiviert. Ein HTTP-429-Fehler wird als ausgeschöpftes Kontingent beziehungsweise Rate-Limit erklärt. Die Anwendung zeigt vorhandene Suchtreffer weiterhin an.

Die Laufzeit der Anwendung liegt auf dem eigenen Laptop. Der Nutzer wählt ein Konto im kostenlosen Tarif. Die Anwendung kann den Abrechnungsstatus des Kontos nicht zuverlässig aus einem Modellnamen ableiten. Vor dem ersten Live-Aufruf werden kostenlose Verfügbarkeit und Konto-Tarif geprüft und dokumentiert. Kostenlose Kontingente können sich ändern.

## Umgang mit Modellantworten

Der Prompt verlangt Antworten aus den bereitgestellten Passagen, deutschsprachige Erklärungen und Quellenkennungen. Bei fehlender Information soll das Modell diese Lücke ausdrücken.

Dokumentinhalte werden als zu untersuchende Daten behandelt. Anweisungen innerhalb eines READMEs erhalten keine Befugnis, Dateien zu verändern oder Werkzeuge aufzurufen. Die erste Version kann Text zurückgeben und Quellen anzeigen. API-Schlüssel werden dem Prompt nicht hinzugefügt.

Eine fehlende oder unbekannte Quellenkennung führt zu einer verständlichen Meldung mit den Originaltreffern. Die Anwendung unterscheidet technische Fehler, fehlende Suchtreffer und eine laut Dokumenten unbeantwortbare Frage.

## Verifikation

Offline-Tests prüfen die Erhaltung von Dokumentinhalt und Quellzeilen, die Suchrangfolge sowie die Behandlung typischer API-Fehler mit einem simulierten Client. Automatisierte Prüfungen benötigen keinen Schlüssel und verbrauchen kein Kontingent.

Die Evaluation hält Dokumentversion, Fragen, Suchverfahren, Promptversion und bei KI-Antworten den Modellnamen fest. Retrieval wird über den Anteil beantwortbarer Fragen mit richtigem Beleg in den ersten drei Treffern gemessen. Die Antwortprüfung bewertet Aussage, Beleg und Umgang mit fehlendem Wissen separat. So bleibt sichtbar, an welcher Stelle ein Fehler entstanden ist.

## Technische Referenzen

Der Stand wurde am 19. November 2026 gegen die folgenden offiziellen Dokumentationsseiten geprüft. Modellverfügbarkeit und konkrete Kontingente werden beim Implementieren erneut geprüft.

- [Groq Quickstart](https://console.groq.com/docs/quickstart)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
