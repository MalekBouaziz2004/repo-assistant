# Projektkontext für Codex

## Ziel und Nutzer

Malek ist Informatikstudent mit Erfahrung in C++, Java und Webentwicklung. Er nutzt KI im Alltag und möchte die Grundlagen von KI und generativer KI durch eigene Projekte verstehen. Codex unterstützt die Implementierung und erklärt die Entscheidungen verständlich auf Deutsch.

Repo Assistant verarbeitet zunächst ein öffentliches README, findet passende Abschnitte und kann daraus über Groq eine Antwort mit überprüfbaren Quellenkennungen erzeugen. Eine spätere Version unterstützt mehrere öffentliche GitHub-Repositories.

Ein aktuelles Beispiel ist „How do I install Requests with pip?“: Die Suche findet den Installationsabschnitt und übergibt ihn mit einer Quellenkennung an die Generierung. Die Frage „Wie starte ich SplitIt?“ ist ein mögliches Beispiel für die spätere Mehr-Repository-Version.

## Verbindliche Rahmenbedingungen

- Das Projektbudget beträgt 0 Euro. Verwende kostenlose Software und kostenlose API-Tarife. Kostenpflichtige Infrastruktur, Guthabenkäufe und automatische Wechsel zu bezahlten Angeboten brauchen einen neuen ausdrücklichen Nutzerauftrag.
- Der Laptop eignet sich laut Nutzer nicht für ein lokales Sprachmodell. Die Textgenerierung erfolgt über eine gehostete API. Die Anwendung und die erste Dokumentsuche laufen auf dem Laptop.
- Groq im kostenlosen Tarif ist die erste Integration. `openai/gpt-oss-20b` ist nach den öffentlichen Anbieterangaben vom 24. November 2026 der dokumentierte Startwert. Die Verfügbarkeit und der Free-Tarif des Nutzerkontos müssen vor einem Live-Aufruf vom Nutzer geprüft werden.
- Modellname und API-Schlüssel kommen aus Umgebungsvariablen. Halte Schlüssel aus Git, Terminalausgaben, Testdaten und Fehlermeldungen heraus.
- Die erste Version arbeitet mit öffentlichen Projektdokumenten. Beim Generieren werden Frage und ausgewählte Textstellen an den API-Anbieter übertragen.
- Open Source und kostenlose API-Nutzung sind unterschiedliche Eigenschaften. Dokumentiere Anbieter und Modell separat und behaupte keine unbegrenzte oder dauerhaft garantierte Gratisnutzung.

## Stand und Einstieg

Stand am 24. November 2026 sind das Einlesen (M1), die Wortsuche samt Offline-Auswertung (M2) und der offline geprüfte Groq-Antwortpfad (M3) implementiert. Ein Live-Aufruf und die inhaltliche Bewertung echter Modellantworten stehen noch aus.

Lies vor einer Implementierung [ARCHITECTURE.md](ARCHITECTURE.md) und [PLAN.md](PLAN.md). Ein Nutzerauftrag zur Planung allein beauftragt keine Implementierung. Die nächsten vorgesehenen Arbeiten sind die bewusste Live-Prüfung von M3 bei bestätigtem Free-Zugang und danach Meilenstein 4.

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
