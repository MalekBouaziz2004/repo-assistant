# Entwicklungs- und Lernplan

## Ziel

Eine Person stellt eine Frage über ein Softwareprojekt und erhält eine Antwort mit einer passenden Dokumentationsquelle. Malek kann erklären, wie das Dokument eingelesen, durchsucht und als Kontext für ein Sprachmodell verwendet wurde.

Die Umsetzung beginnt mit einem README im Terminal und wächst anhand gemessener Ergebnisse. Die Reihenfolge ist eine Lernempfehlung und kann durch einen Nutzerauftrag angepasst werden.

## Fortschritt

- [x] Projektkontext und Architektur dokumentiert
- [x] Meilenstein 1 — README einlesen und Abschnitte anzeigen
- [x] Meilenstein 2 — Suche und Referenzfragen
- [ ] Meilenstein 3 — KI-Antwort mit Quellen
- [ ] Meilenstein 4 — Mehrere öffentliche GitHub-Projekte
- [ ] Meilenstein 5 — Qualität vergleichen und Portfolio-Demo

## Meilenstein 1 — Dokumente verstehen

**Lernziel** ist zu verstehen, wie Text zu durchsuchbaren Abschnitten wird. Ein Chunk ist ein Textabschnitt, der zusammen mit seinem Herkunftsnachweis gespeichert wird.

**Umsetzung**

1. Richte ein kleines Python-Projekt mit dokumentierter virtueller Umgebung ein. Wähle die Python-Version passend zur vorhandenen Installation und den benötigten Paketen.
2. Verwende eine öffentliche README-Kopie als Beispieldokument. Halte Repository-URL, Dateipfad und den zugehörigen Commit fest. Übernimm dessen ursprüngliche Überschriften und Formatierung.
3. Teile das Dokument an Markdown-Überschriften. Erkenne Codeblöcke, damit eine Zeile mit einem Hash-Zeichen darin keine neue Überschrift erzeugt.
4. Begrenze zu lange Abschnitte an sinnvollen Absatz- oder Zeilengrenzen. Bewahre Originalzeilen und Überschrift pro Teilabschnitt.
5. Gib Abschnittskennung, Überschrift, Zeilenbereich und Text über einen Terminalbefehl aus. Leere Dateien und fehlende Pfade erzeugen verständliche Meldungen.

**Fertig**, wenn ein anderer Entwickler mit den README-Befehlen das Beispieldokument einlesen kann, alle nicht leeren Inhalte erhalten bleiben und die angezeigten Zeilen zur Originaldatei passen.

**Prüfung** mit einem kurzen Markdown-Beispiel einschließlich Einleitung, Überschriften, langem Abschnitt und Codeblock.

**Übung** — Füge eine Überschrift hinzu und beobachte, wie sich die Abschnitte ändern.

**Verifizierter Stand nach M1 am 19. November 2026:** Das Python-3.12-Paket liest ein lokales UTF-8-README, trennt Überschriften außerhalb von Codeblöcken und teilt lange Abschnitte an Leerzeilen oder ganzen Zeilen. Die Terminalausgabe enthält Abschnittskennung, Überschrift, Originalzeilen und Text. Das öffentliche `psf/requests`-README ist auf Commit `3c7baaa05ab4aa49cc819ce3a819d260de19c157` fixiert; der lokale Git-Blob-Hash `4e5c44555c02f127cd0cca2efa8b22716c78ee23` stimmt mit dem GitHub-Blob überein. Der dokumentierte Startbefehl zeigte 5 Abschnitte. Sechs Offline-Tests bestanden, darunter Einleitung, langer Abschnitt, Codeblock, unveränderte Zeilen sowie fehlende und leere Datei. Eine einzelne überlange Originalzeile bleibt vollständig und kann das Zeichenlimit überschreiten. Zu diesem Zeitpunkt gab es noch keine Suche und keinen API-Aufruf.

## Meilenstein 2 — Suche und Referenzfragen

**Lernziel** ist Retrieval, also das Auffinden relevanter Textstellen, und seine messbare Qualität.

**Umsetzung**

1. Lege vor der Optimierung zehn Referenzfragen mit erwarteten Quellzeilen oder der Markierung „im Dokument unbeantwortbar“ an. Nimm deutsche und englische Fragen auf.
2. Baue eine einfache Suche auf Basis normalisierter Suchwörter und Wortübereinstimmungen. Die Bewertung und eine feste Reihenfolge bei Gleichstand müssen erklärbar sein.
3. Zeige bis zu drei Treffer mit Bewertung und Quelle. Bei fehlenden Wortübereinstimmungen bleibt die Trefferliste leer.
4. Miss auf den beantwortbaren Fragen den Anteil, bei dem ein erwarteter Beleg unter den ersten drei Treffern liegt. Das ist die hier verwendete Recall@3-Auswertung.
5. Halte die erste Messung als Ausgangswert fest. Dokumentiere ein Beispiel, bei dem unterschiedliche Wörter oder Sprachen die Suche scheitern lassen.

**Fertig**, wenn eine Frage über den Terminaleinstieg gesucht werden kann und sich die Auswertung ohne Netzwerk wiederholen lässt. Die Bewertung misst Wortübereinstimmung und ist keine Wahrscheinlichkeit für eine richtige Antwort.

**Prüfung** von Trefferrangfolge, Gleichstand, leerer Frage und fehlenden Treffern.

**Übung** — Vergleiche „record payments“ und „Zahlungen verbuchen“ bei einem englischen Dokument.

**Verifizierter Stand nach M2 am 19. November 2026:** `data/evaluation/questions.json` enthält zehn vor der Suchimplementierung festgelegte Fragen zum gepinnten Requests-README: acht mit geprüften Originalzeilen und zwei als „im Dokument unbeantwortbar“. Die Fragen sind deutsch und englisch. Die lokale Suche zählt unterschiedliche normalisierte Wortüberschneidungen zwischen Frage und Chunk-Überschrift samt Text. Gleichstände werden nach Originalzeile und Abschnittskennung geordnet; ohne Wortüberschneidung gibt es keinen Treffer. Der Terminalbefehl `python -m repo_assistant.cli --question "How do I install Requests with pip?"` zeigte den Installationsbeleg aus Zeilen 30–39 auf Rang 1 mit Wertung 3 und gepinntem Quellenlink. `python -m repo_assistant.cli --question "Kann die Bibliothek Verbindungen wiederverwenden?"` zeigte keinen Treffer, obwohl Zeile 44 die fachlich passende englische Stelle „Keep-Alive & Connection Pooling“ enthält. Das ist die dokumentierte Sprachgrenze dieser Ausgangsversion.

Der reproduzierbare Befehl `python -m repo_assistant.cli --evaluate` prüfte zuerst den Datei-Hash und ergab **Recall@3 = 7/8 = 87,5 %** bei 1200 Zeichen pro Chunk. Q01–Q04 und Q06–Q08 fanden ihren vollständigen Beleg auf Rang 1; Q05 fand keinen Beleg. Q09 und Q10 sind unbeantwortbar und wurden aus Recall@3 ausgeschlossen; für beide lieferte die Wortsuche trotzdem drei Treffer. Die Wertung ist keine Antwortwahrscheinlichkeit, und diese Messung bewertet keine generierte Antwort. Alle zwölf Offline-Tests, einschließlich der sechs M1-Tests, bestanden ohne API-Schlüssel und ohne Anbieteraufruf.

## Meilenstein 3 — Antworten mit einer kostenlosen KI-API

**Lernziel** ist RAG, das Zusammenspiel aus gefundenen Textstellen und einer daraus erzeugten Antwort.

**Umsetzung**

1. Prüfe, welches Textmodell im Groq-Free-Tarif des Nutzerkontos verfügbar ist. Dokumentiere die Auswahl mit Datum. Der Nutzer richtet den kostenlosen Zugang selbst ein.
2. Ergänze eine Beispielkonfiguration mit leeren Werten für GROQ_API_KEY und GROQ_MODEL. Prüfe, dass die echte .env-Datei ignoriert wird.
3. Ergänze einen kleinen Groq-Client. Begrenze Kontextlänge, Antwortlänge und Wartezeit. Deaktiviere automatische SDK-Wiederholungen für diese erste Version.
4. Übergebe nur Frage und ausgewählte Abschnitte mit stabilen Quellenkennungen. Fordere eine deutschsprachige Antwort mit Belegen und eine klare Aussage bei fehlenden Informationen an.
5. Prüfe, dass angeführte Quellenkennungen im übergebenen Kontext vorkommen. Erzeuge Links aus den gespeicherten Quelldaten. Ungültige Quellen führen zu einer Meldung und den tatsächlich gefundenen Passagen.
6. Bei leerer Trefferliste entfällt der Modellaufruf. Bei Rate-Limit, fehlendem Modell, fehlendem Schlüssel, Netzwerkfehler oder Timeout gibt es eine verständliche Meldung. Die Suchtreffer bleiben verfügbar.
7. Führe einen bewusst gestarteten Live-Test aus, sobald ein kostenloser API-Zugang vorhanden ist. Prüfe die zehn Referenzfragen zusätzlich auf korrekte Aussagen, passende Belege und angemessene Antworten bei fehlender Information.

**Fertig**, wenn eine dokumentierte Frage eine belegte Antwort liefert und Fehlerfälle offline mit einem simulierten Client geprüft sind. Ist kein Zugang vorhanden, dokumentiere die Live-Prüfung als ausstehend.

**Übung** — Vergleiche eine Antwort mit vollständigem und eine mit unpassendem Kontext.

## Meilenstein 4 — Mehrere öffentliche GitHub-Projekte

**Lernziel** ist die nachvollziehbare Zuordnung von Wissen zu Repository, Datei und Version.

**Umsetzung** — Importiere ausdrücklich ausgewählte öffentliche GitHub-READMEs. Ermittle Standardbranch und Commit, speichere Dokumente samt Herkunft lokal und ermögliche eine Suche je Repository oder über alle importierten Dokumente. Ein erneuter Import aktualisiert den Bestand ohne Duplikate. Abruffehler erhalten die letzte vollständige Version.

**Fertig**, wenn mindestens zwei Projekte unterscheidbare Quellen liefern und ein Dokumentwechsel über Commit und erneuten Import nachvollziehbar ist.

**Übung** — Stelle dieselbe Frage einmal für ein einzelnes Repository und einmal für den gesamten Bestand.

## Meilenstein 5 — Vergleich und Portfolio

**Lernziel** ist die Beurteilung einer Verbesserung anhand derselben Fragen.

Untersuche anhand des dokumentierten Suchfehlers, ob BM25 oder eine Suche mit Embeddings sinnvoll ist. BM25 gewichtet unter anderem seltene Wörter. Embeddings stellen Texte als Zahlenvektoren dar und ermöglichen Vergleiche nach Bedeutung.

Prüfe vor der Auswahl einer Embedding-Lösung deren Ressourcenbedarf und kostenlose Nutzbarkeit. Eine kleine CPU-Lösung kann auf dem Laptop getestet werden, sofern dessen Ausstattung reicht. Eine kostenlose gehostete Lösung ist ebenfalls möglich. Erhalte die bisherige Suche als Vergleich.

**Fertig**, wenn eine Ausgangsversion und eine Änderung auf demselben Dokumentstand verglichen wurden. Dokumentiere Trefferqualität, Antwortfehler, Laufzeit und API-Aufrufe. Wähle einige zusätzliche, vorher unbenutzte Fragen, um die Verbesserung zu prüfen. Ergänze README und eine kurze Demo mit einem gelungenen und einem fehlgeschlagenen Fall.

## Mögliche spätere Erweiterungen

Eine Weboberfläche, PDF-Verarbeitung, Quellcodefragen und weitere Anbieter können nach der ersten Demo bewertet werden. Sie erweitern den hier beschriebenen Funktionsumfang und sind eigenständige spätere Aufgaben.
