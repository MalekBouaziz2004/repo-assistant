"""Terminal entry point for inspecting Markdown chunks."""

import argparse
import json
from pathlib import Path

from .documents import read_document, split_markdown
from .evaluation import evaluate, load_questions
from .retrieval import search


DEFAULT_DOCUMENT = Path("data/documents/requests.README.md")
DEFAULT_SOURCE = Path("data/documents/requests.source.json")
DEFAULT_QUESTIONS = Path("data/evaluation/questions.json")


def _source(path: Path, start_line: int, end_line: int) -> str:
    if path.resolve() == DEFAULT_DOCUMENT.resolve():
        metadata = json.loads(DEFAULT_SOURCE.read_text(encoding="utf-8"))
        return f"{metadata['source_url']}#L{start_line}-L{end_line}"
    return f"{path}:L{start_line}-L{end_line}"


def main() -> int:
    parser = argparse.ArgumentParser(description="README in Abschnitte mit Originalzeilen aufteilen")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_DOCUMENT, help="Pfad zur Markdown-Datei")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximale Zeichen je Abschnitt (Standard: 1200)")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--question", help="Frage stellen und bis zu drei Suchtreffer anzeigen")
    action.add_argument("--evaluate", action="store_true", help="Zehn Referenzfragen offline auswerten")
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
