"""A transparent baseline search using distinct word overlap."""

from dataclasses import dataclass
import re
import unicodedata

from .documents import Chunk


@dataclass(frozen=True)
class Hit:
    rank: int
    score: int
    chunk: Chunk


def words(text: str) -> set[str]:
    """Case-fold, remove accents and split punctuation into word boundaries."""
    normalized = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return set(re.findall(r"[^\W_]+", without_accents, flags=re.UNICODE))


def search(question: str, chunks: list[Chunk], limit: int = 3) -> list[Hit]:
    """Rank by the count of unique shared words; break ties by source order."""
    if not question.strip() or not words(question):
        raise ValueError("Bitte eine nicht leere Frage eingeben.")
    if limit < 1:
        raise ValueError("Die Trefferzahl muss größer als 0 sein.")
    query_words = words(question)
    scored = [
        (len(query_words & words(chunk.heading + " " + chunk.text)), chunk)
        for chunk in chunks
    ]
    matched = [(score, chunk) for score, chunk in scored if score > 0]
    matched.sort(key=lambda item: (-item[0], item[1].start_line, item[1].chunk_id))
    return [Hit(rank, score, chunk) for rank, (score, chunk) in enumerate(matched[:limit], 1)]
