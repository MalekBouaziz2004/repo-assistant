"""Repeatable offline Recall@3 against pinned README line references."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .documents import Chunk
from .retrieval import search


@dataclass(frozen=True)
class CaseResult:
    question_id: str
    answerable: bool
    matching_rank: int | None
    hits_count: int


@dataclass(frozen=True)
class EvaluationResult:
    cases: list[CaseResult]
    found: int
    answerable: int

    @property
    def recall_at_3(self) -> float:
        return self.found / self.answerable if self.answerable else 0.0


def git_blob_sha(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_questions(path: Path, document_path: Path, text: str) -> dict:
    try:
        reference = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Referenzfragen nicht lesbar: {path}") from error
    if reference["document_id"] != document_path.stem or reference["blob_sha"] != git_blob_sha(text):
        raise ValueError("Referenzfragen und README-Version passen nicht zusammen.")
    lines = text.splitlines()
    for case in reference["questions"]:
        for evidence in case["evidence"]:
            start, end = evidence["start_line"], evidence["end_line"]
            if not (1 <= start <= end <= len(lines)) or not any(lines[start - 1:end]):
                raise ValueError(f"Ungültige Belegzeilen in {case['id']}.")
    return reference


def evaluate(reference: dict, chunks: list[Chunk]) -> EvaluationResult:
    cases: list[CaseResult] = []
    for case in reference["questions"]:
        hits = search(case["question"], chunks, limit=3)
        evidence = case["evidence"]
        matching_rank = next((
            hit.rank for hit in hits
            if any(hit.chunk.start_line <= span["start_line"]
                   and hit.chunk.end_line >= span["end_line"] for span in evidence)
        ), None)
        cases.append(CaseResult(case["id"], bool(evidence), matching_rank, len(hits)))
    answerable = sum(case.answerable for case in cases)
    found = sum(case.matching_rank is not None for case in cases if case.answerable)
    return EvaluationResult(cases, found, answerable)
