"""Read Markdown and retain exact source lines while splitting it."""

from dataclasses import dataclass
from pathlib import Path
import re


HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


@dataclass(frozen=True)
class Chunk:
    document_id: str
    chunk_id: str
    heading: str
    start_line: int
    end_line: int
    text: str


def read_document(path: Path) -> str:
    """Read UTF-8 without changing line endings or hiding useful errors."""
    try:
        with path.open("r", encoding="utf-8", newline="") as document:
            text = document.read()
    except FileNotFoundError as error:
        raise ValueError(f"Datei nicht gefunden: {path}") from error
    except IsADirectoryError as error:
        raise ValueError(f"Pfad ist ein Verzeichnis: {path}") from error
    except UnicodeError as error:
        raise ValueError(f"Datei ist nicht als UTF-8 lesbar: {path}") from error
    if not text.strip():
        raise ValueError(f"Datei ist leer: {path}")
    return text


def _sections(lines: list[str]) -> list[tuple[str, int, list[str]]]:
    sections: list[tuple[str, int, list[str]]] = []
    heading = "Einleitung"
    start = 1
    current: list[str] = []
    fence_char = ""
    fence_length = 0

    for number, line in enumerate(lines, 1):
        bare = line.rstrip("\r\n")
        fence = FENCE.match(bare)
        if fence_char:
            if fence and fence.group(1)[0] == fence_char:
                remainder = bare[fence.end():]
                if len(fence.group(1)) >= fence_length and not remainder.strip():
                    fence_char = ""
        elif fence:
            fence_char = fence.group(1)[0]
            fence_length = len(fence.group(1))
        else:
            match = HEADING.match(bare)
            if match:
                if current:
                    sections.append((heading, start, current))
                heading = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2) or "").strip() or "Ohne Titel"
                start = number
                current = []
        current.append(line)

    if current:
        sections.append((heading, start, current))
    return sections


def _parts(lines: list[str], max_chars: int) -> list[tuple[int, int]]:
    """Prefer a blank-line boundary; otherwise use the next whole line."""
    parts: list[tuple[int, int]] = []
    start = 0
    while start < len(lines):
        end = start
        size = 0
        while end < len(lines) and (size + len(lines[end]) <= max_chars or end == start):
            size += len(lines[end])
            end += 1
        if end < len(lines):
            blank = next((i for i in range(end - 1, start, -1) if not lines[i].strip()), None)
            if blank is not None:
                end = blank + 1
        parts.append((start, end))
        start = end
    return parts


def split_markdown(text: str, document_id: str, max_chars: int = 1200) -> list[Chunk]:
    """Split on headings and size limits, preserving every original line once."""
    if max_chars < 1:
        raise ValueError("max_chars muss größer als 0 sein")
    lines = text.splitlines(keepends=True)
    chunks: list[Chunk] = []
    for heading, section_start, section_lines in _sections(lines):
        for first, last in _parts(section_lines, max_chars):
            chunks.append(Chunk(
                document_id=document_id,
                chunk_id=f"{document_id}-{len(chunks) + 1:03d}",
                heading=heading,
                start_line=section_start + first,
                end_line=section_start + last - 1,
                text="".join(section_lines[first:last]),
            ))
    return chunks
