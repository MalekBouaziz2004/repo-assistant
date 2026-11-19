"""Meaningful checks for search ranking and the pinned offline baseline."""

import locale
from pathlib import Path
import subprocess
import sys
import unittest

from repo_assistant.documents import Chunk, read_document, split_markdown
from repo_assistant.evaluation import evaluate, load_questions
from repo_assistant.retrieval import search, words


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "data/documents/requests.README.md"
QUESTIONS = ROOT / "data/evaluation/questions.json"


def chunk(number: int, text: str) -> Chunk:
    return Chunk("test", f"test-{number}", "Heading", number, number, text)


class RetrievalTests(unittest.TestCase):
    def test_ranking_and_source_order_on_ties(self) -> None:
        chunks = [chunk(30, "alpha"), chunk(20, "alpha beta"), chunk(10, "alpha")]
        hits = search("alpha beta", chunks)
        self.assertEqual([(hit.chunk.start_line, hit.score) for hit in hits], [(20, 2), (10, 1), (30, 1)])
        self.assertEqual([hit.rank for hit in hits], [1, 2, 3])

    def test_normalization_and_no_match(self) -> None:
        self.assertEqual(words("ÜBER Café, cafe!"), {"uber", "cafe"})
        self.assertEqual(search("Zahlungen verbuchen", [chunk(1, "Connection Pooling")]), [])

    def test_empty_question(self) -> None:
        with self.assertRaisesRegex(ValueError, "nicht leere Frage"):
            search("  \t", [chunk(1, "alpha")])

    def test_pinned_reference_lines_and_baseline(self) -> None:
        text = read_document(DOCUMENT)
        reference = load_questions(QUESTIONS, DOCUMENT, text)
        self.assertEqual(len(reference["questions"]), 10)
        self.assertEqual(sum(not case["evidence"] for case in reference["questions"]), 2)
        self.assertEqual({case["language"] for case in reference["questions"]}, {"de", "en"})
        chunks = split_markdown(text, DOCUMENT.stem, reference["max_chars"])
        result = evaluate(reference, chunks)
        self.assertEqual((result.found, result.answerable, result.recall_at_3), (7, 8, 0.875))
        self.assertEqual([case.question_id for case in result.cases if case.answerable and case.matching_rank is None], ["Q05"])

    def test_reference_set_rejects_other_document_version(self) -> None:
        text = read_document(DOCUMENT)
        with self.assertRaisesRegex(ValueError, "README-Version"):
            load_questions(QUESTIONS, DOCUMENT, text + "changed\n")

    def test_search_and_evaluation_via_terminal(self) -> None:
        for arguments, expected in [
            (["--question", "How do I install Requests with pip?"], "#L30-L39"),
            (["--question", "Zahlungen verbuchen"], "keine Treffer"),
            (["--evaluate"], "Recall@3: 7/8 = 87.5%"),
        ]:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, "-m", "repo_assistant.cli", *arguments],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding=locale.getencoding(),
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)


if __name__ == "__main__":
    unittest.main()
