"""Terminal entry point for inspecting Markdown chunks."""

import argparse
from pathlib import Path

from .documents import read_document, split_markdown


DEFAULT_DOCUMENT = Path("data/documents/requests.README.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="README in Abschnitte mit Originalzeilen aufteilen")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_DOCUMENT, help="Pfad zur Markdown-Datei")
    parser.add_argument("--max-chars", type=int, default=1200, help="Maximale Zeichen je Abschnitt (Standard: 1200)")
    args = parser.parse_args()
    try:
        text = read_document(args.path)
        chunks = split_markdown(text, args.path.stem, args.max_chars)
    except ValueError as error:
        parser.exit(2, f"Fehler: {error}\n")

    for chunk in chunks:
        print(f"[{chunk.chunk_id}] {chunk.heading} | Zeilen {chunk.start_line}-{chunk.end_line}")
        print(chunk.text, end="" if chunk.text.endswith("\n") else "\n")
        print()
    print(f"{len(chunks)} Abschnitte aus {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
