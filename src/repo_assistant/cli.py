"""Terminal entry point for inspecting Markdown chunks."""

import argparse
import json
from pathlib import Path
import sys

from .documents import read_document, split_markdown
from .evaluation import evaluate, git_blob_sha, load_questions
from .generation import GenerationError, GroqClient, generate_answer
from .retrieval import search


DEFAULT_DOCUMENT = Path("data/documents/requests.README.md")
DEFAULT_SOURCE = Path("data/documents/requests.source.json")
DEFAULT_QUESTIONS = Path("data/evaluation/questions.json")


def _source(path: Path, start_line: int, end_line: int) -> str:
    if path.resolve() == DEFAULT_DOCUMENT.resolve():
        metadata = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        return f"{metadata['source_url']}#L{start_line}-L{end_line}"
    return f"{path}:L{start_line}-L{end_line}"


def _show_passages(hits, path: Path) -> None:
    print("Gefundene Textstellen zur eigenen Prüfung:")
    for hit in hits:
        chunk = hit.chunk
        print(f"- [{chunk.chunk_id}] {chunk.heading}, {path}:L{chunk.start_line}-L{chunk.end_line}")
        print(chunk.text)


def main() -> int:
    parser = argparse.ArgumentParser(description="README in Abschnitte mit Originalzeilen aufteilen")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_DOCUMENT, help="Pfad zur Markdown-Datei")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximale Zeichen je Abschnitt (Standard: 1200)")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--question", help="Frage stellen und bis zu drei Suchtreffer anzeigen")
    action.add_argument("--evaluate", action="store_true", help="Zehn Referenzfragen offline auswerten")
    action.add_argument("--answer", help="Mit Groq aus gefundenen Passagen antworten")
    action.add_argument("--live-test", action="store_true", help="Bewusster Live-Test mit Referenzfrage Q01 (ein API-Aufruf)")
    args = parser.parse_args()
    try:
        text = read_document(args.path)
        chunks = split_markdown(text, args.path.stem, args.max_chars)
        if args.evaluate:
            reference = load_questions(DEFAULT_QUESTIONS, args.path, text)
            if args.max_chars != reference["max_chars"]:
                raise ValueError(f"Die Auswertung benötigt --max-chars {reference['max_chars']}.")
            result = evaluate(reference, chunks)
        elif args.question is not None:
            hits = search(args.question, chunks)
        elif args.answer is not None or args.live_test:
            if args.live_test:
                reference = load_questions(DEFAULT_QUESTIONS, args.path, text)
                answer_question = reference["questions"][0]["question"]
            else:
                answer_question = args.answer
            hits = search(answer_question, chunks)
    except ValueError as error:
        parser.exit(2, f"Fehler: {error}\n")

    if args.evaluate:
        print(f"Dokument: {reference['repository_url']}/blob/{reference['commit']}/{reference['source_path']}")
        print("Verfahren: unterschiedliche gemeinsame Wörter; Top 3; max. 1200 Zeichen je Chunk")
        for case in result.cases:
            if not case.answerable:
                outcome = f"im Dokument unbeantwortbar (nicht in Recall@3; {case.hits_count} Treffer)"
            elif case.matching_rank is None:
                outcome = "kein Beleg unter Top 3"
            else:
                outcome = f"Beleg auf Rang {case.matching_rank}"
            print(f"{case.question_id}: {outcome}")
        print(f"Recall@3: {result.found}/{result.answerable} = {result.recall_at_3:.1%}")
        return 0

    if args.answer is not None or args.live_test:
        if not hits:
            print("Keine passenden Textstellen gefunden. Die Frage bleibt unbeantwortet; kein API-Aufruf.")
            return 0
        try:
            if args.path.resolve() != DEFAULT_DOCUMENT.resolve():
                raise GenerationError("KI-Antworten sind derzeit nur für das mitgelieferte öffentliche README verfügbar.")
            metadata = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
            if metadata["document_id"] != args.path.stem or metadata["blob_sha"] != git_blob_sha(text):
                raise GenerationError("Das README stimmt nicht mit der gespeicherten öffentlichen Quelle überein.")
            client = GroqClient.from_environment()
            result = generate_answer(answer_question, hits, client, metadata["source_url"])
        except (OSError, ValueError, KeyError) as error:
            print("Fehler: Die Quelldaten sind nicht lesbar oder unvollständig.", file=sys.stderr)
            _show_passages(hits, args.path)
            return 1
        except GenerationError as error:
            print(f"Fehler: {error}", file=sys.stderr)
            _show_passages(hits, args.path)
            return 1
        print(f"Antwort: {result.answer}")
        if result.sources:
            print("Quellen:")
            for source in result.sources:
                print(f"- [{source.source_id}] {source.url}")
        else:
            _show_passages(hits, args.path)
        if args.live_test:
            print("Live-Test: Antwort empfangen und Quellenkennungen geprüft; Inhalt manuell prüfen.")
        return 0

    if args.question is not None:
        if not hits:
            print("Keine Wortübereinstimmung und damit keine Treffer.")
            return 0
        for hit in hits:
            chunk = hit.chunk
            print(f"{hit.rank}. [{chunk.chunk_id}] {chunk.heading} | Wertung {hit.score}")
            print(f"Quelle: {_source(args.path, chunk.start_line, chunk.end_line)}")
            print(chunk.text, end="" if chunk.text.endswith("\n") else "\n")
            print()
        return 0

    for chunk in chunks:
        print(f"[{chunk.chunk_id}] {chunk.heading} | Zeilen {chunk.start_line}-{chunk.end_line}")
        print(chunk.text, end="" if chunk.text.endswith("\n") else "\n")
        print()
    print(f"{len(chunks)} Abschnitte aus {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
