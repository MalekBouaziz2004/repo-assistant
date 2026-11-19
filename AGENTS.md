# Projektkontext für Codex

## Ziel und Nutzer

Malek ist Informatikstudent mit Erfahrung in C++, Java und Webentwicklung. Er nutzt KI im Alltag und möchte die Grundlagen von KI und generativer KI durch eigene Projekte verstehen. Codex unterstützt die Implementierung und erklärt die Entscheidungen verständlich auf Deutsch.

Repo Assistant beantwortet Fragen zu Softwareprojekten anhand ihrer Dokumentation. Die erste Version verarbeitet ein README, findet passende Abschnitte und beantwortet Fragen mit überprüfbaren Quellen. Eine spätere Version unterstützt mehrere öffentliche GitHub-Repositories.

Ein Beispiel ist die Frage „Wie starte ich SplitIt?“. Die Anwendung findet den Abschnitt zum Start mit Docker und verwendet ihn als Grundlage der Antwort.

## Verbindliche Rahmenbedingungen

- Das Projektbudget beträgt 0 Euro. Verwende kostenlose Software und kostenlose API-Tarife. Kostenpflichtige Infrastruktur, Guthabenkäufe und automatische Wechsel zu bezahlten Angeboten brauchen einen neuen ausdrücklichen Nutzerauftrag.
- Der Laptop eignet sich laut Nutzer nicht für ein lokales Sprachmodell. Die Textgenerierung erfolgt über eine gehostete API. Die Anwendung und die erste Dokumentsuche laufen auf dem Laptop.
- Groq im kostenlosen Tarif ist die vorgeschlagene erste Integration. Das konkret verfügbare Modell muss bei der Implementierung anhand der aktuellen Anbieterinformationen und des Nutzerkontos gewählt werden.
- Modellname und API-Schlüssel kommen aus Umgebungsvariablen. Halte Schlüssel aus Git, Terminalausgaben, Testdaten und Fehlermeldungen heraus.
- Die erste Version arbeitet mit öffentlichen Projektdokumenten. Beim Generieren werden Frage und ausgewählte Textstellen an den API-Anbieter übertragen.
- Open Source und kostenlose API-Nutzung sind unterschiedliche Eigenschaften. Dokumentiere Anbieter und Modell separat und behaupte keine unbegrenzte oder dauerhaft garantierte Gratisnutzung.

## Stand und Einstieg

Stand am 19. November 2026 ist die Planungsphase. Im Repository gibt es noch keine implementierte Anwendung.

Lies vor einer Implementierung [ARCHITECTURE.md](ARCHITECTURE.md) und [PLAN.md](PLAN.md). Der nächste vorgesehene Auftrag ist Meilenstein 1 aus dem Plan. Ein Nutzerauftrag zur Planung allein beauftragt keine Implementierung.

Prüfe bei späteren Arbeiten zuerst den tatsächlichen Code und den Plan. Vermerke abgeschlossene Meilensteine und überprüfbare Ergebnisse in PLAN.md. Trenne dabei bestehende Funktionen und geplante Erweiterungen deutlich.

## Zusammenarbeit und Lernen

- Erkläre vor einer Änderung knapp, welches Problem sie löst und welche Dateien betroffen sind.
- Implementiere den beauftragten Umfang vollständig in nachvollziehbaren Schritten. Bei einem Auftrag für mehrere Meilensteine arbeite diese der Reihe nach ab.
- Erkläre neue Begriffe beim ersten Auftreten mit einem Beispiel aus dieser Anwendung.
- Zeige nach der Änderung den Datenfluss an einer konkreten Frage und nenne den passenden Ausführungsbefehl.
- Fasse die Verifikation und ihre Ergebnisse zusammen. Kennzeichne live nicht geprüfte API-Aufrufe.
- Gib pro Meilenstein eine kleine Übung, etwa einen Suchbegriff zu verändern und die Treffer zu vergleichen. Eine Verständnisfrage ist eine Lernhilfe und keine zusätzliche Freigabe.
- Halte Code und Bezeichner auf Englisch. Erklärungen, Lernnotizen und die erste Benutzeroberfläche sind auf Deutsch.

## Implementierungsstil

Verwende übersichtliche Python-Module und kleine Funktionen. Beginne mit Standardbibliothek und einer Terminaloberfläche. Füge Abhängigkeiten hinzu, wenn der aktuelle Meilenstein sie benötigt.

Die Architektur beschreibt einen schrittweisen Zielaufbau. Lege Module erst an, wenn sie verwendet werden. Die erste Suche verwendet nachvollziehbare Wortübereinstimmungen. Embeddings und Vektorsuche werden später anhand einer gemessenen Schwäche untersucht.

Prüfe konkrete Fehlerfälle mit kleinen, aussagekräftigen Tests. Automatisierte Tests laufen ohne API-Schlüssel und ohne Anbieteraufrufe. Ein bewusst gestarteter Live-Test kann später eine Anfrage aus dem kostenlosen Kontingent verwenden.

## Fertigstellung eines Implementierungsauftrags

Der beauftragte Ablauf funktioniert über den dokumentierten Einstieg. Neue Funktionen haben passende Beispiele und aussagekräftige Prüfungen. Fehlermeldungen helfen beim nächsten Schritt. PLAN.md bildet den verifizierten Fortschritt ab, und README.md erklärt den jeweils vorhandenen Stand.
