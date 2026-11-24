"""Offline RAG checks with simulated Groq responses and transport."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib import error

from repo_assistant import cli
from repo_assistant.documents import Chunk, read_document, split_markdown
from repo_assistant.evaluation import load_questions
from repo_assistant.generation import (
    API_URL, MAX_COMPLETION_TOKENS, MAX_CONTEXT_CHARS, TIMEOUT_SECONDS,
    GenerationError, GroqClient, generate_answer, prepare_passages,
)
from repo_assistant.retrieval import Hit, search


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "data/documents/requests.README.md"
QUESTIONS = ROOT / "data/evaluation/questions.json"
SOURCE_URL = "https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md"


class FakeClient:
    def __init__(self, response: dict):
        self.response = response
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return json.dumps(self.response)


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        text = read_document(DOCUMENT)
        cls.reference = load_questions(QUESTIONS, DOCUMENT, text)
        cls.chunks = split_markdown(text, DOCUMENT.stem)

    def case_hits(self, question_id: str) -> tuple[str, list[Hit]]:
        question = next(case["question"] for case in self.reference["questions"] if case["id"] == question_id)
        return question, search(question, self.chunks)

    def test_answered_reference_question_uses_only_selected_passages(self) -> None:
        question, hits = self.case_hits("Q01")
        client = FakeClient({"answerable": True, "answer": "Mit `python -m pip install requests` installieren.", "sources": ["S1"]})
        result = generate_answer(question, hits, client, SOURCE_URL)
        self.assertTrue(result.answerable)
        self.assertEqual(result.sources[0].url, SOURCE_URL + "#L30-L39")
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0][0]["role"], "system")
        self.assertIn(question, client.calls[0][1]["content"])
        self.assertIn("[S1]", client.calls[0][1]["content"])
        self.assertIn("python -m pip install requests", client.calls[0][1]["content"])
        self.assertNotIn("GROQ_API_KEY", str(client.calls))

    def test_no_evidence_skips_client(self) -> None:
        question, hits = self.case_hits("Q05")
        self.assertEqual(hits, [])
        client = FakeClient({"answerable": True, "answer": "invented", "sources": ["S1"]})
        result = generate_answer(question, hits, client, SOURCE_URL)
        self.assertTrue(result.no_hits)
        self.assertEqual(client.calls, [])

    def test_word_hits_can_still_be_unanswerable(self) -> None:
        question, hits = self.case_hits("Q10")
        self.assertTrue(hits)
        client = FakeClient({"answerable": False, "answer": "Die Lizenz steht nicht im bereitgestellten README.", "sources": []})
        result = generate_answer(question, hits, client, SOURCE_URL)
        self.assertFalse(result.answerable)
        self.assertEqual(result.sources, [])
        self.assertTrue(result.passages)
        self.assertEqual(len(client.calls), 1)

    def test_unknown_or_missing_source_rejects_answer(self) -> None:
        question, hits = self.case_hits("Q01")
        for response in [
            {"answerable": True, "answer": "Installiere mit pip.", "sources": []},
            {"answerable": True, "answer": "Installiere mit pip [S9].", "sources": ["S1"]},
        ]:
            with self.subTest(response=response):
                with self.assertRaisesRegex(GenerationError, "Quellenkennungen"):
                    generate_answer(question, hits, FakeClient(response), SOURCE_URL)

    def test_context_limit_keeps_whole_lines_and_source_mapping(self) -> None:
        huge = Chunk("doc", "huge", "Long", 1, 1, "x" * (MAX_CONTEXT_CHARS + 1))
        small = Chunk("doc", "small", "Short", 2, 2, "useful\n")
        passages, context = prepare_passages([Hit(1, 2, huge), Hit(2, 1, small)], SOURCE_URL)
        self.assertLessEqual(len(context), MAX_CONTEXT_CHARS)
        self.assertEqual([(item.source_id, item.hit.chunk.chunk_id) for item in passages], [("S1", "small")])

    def test_client_sends_one_bounded_request_without_retries(self) -> None:
        calls = []
        def transport(request, timeout):
            calls.append((request, timeout))
            response = {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]}
            return io.BytesIO(json.dumps(response).encode("utf-8"))
        client = GroqClient("dummy-key", "openai/gpt-oss-20b", transport)
        self.assertEqual(client.complete([{"role": "user", "content": "test"}]), "{}")
        self.assertEqual(len(calls), 1)
        payload = json.loads(calls[0][0].data)
        self.assertEqual(calls[0][1], TIMEOUT_SECONDS)
        self.assertEqual(payload["max_completion_tokens"], MAX_COMPLETION_TOKENS)
        self.assertEqual(payload["reasoning_effort"], "low")
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    def test_provider_failures_do_not_echo_secret_or_response(self) -> None:
        failures = [
            (error.HTTPError(API_URL, 400, "secret-provider-body", None, None), "Modell oder Anfrage"),
            (error.HTTPError(API_URL, 401, "secret-provider-body", None, None), "API-Schlüssel"),
            (error.HTTPError(API_URL, 429, "secret-provider-body", None, None), "Rate-Limit"),
            (error.HTTPError(API_URL, 404, "secret-provider-body", None, None), "Modell"),
            (TimeoutError(), "30 Sekunden"),
            (error.URLError(TimeoutError()), "30 Sekunden"),
            (error.URLError("secret-provider-body"), "Netzwerkfehler"),
        ]
        for failure, expected in failures:
            with self.subTest(expected=expected):
                def transport(request, timeout):
                    raise failure
                with self.assertRaises(GenerationError) as raised:
                    GroqClient("dummy-key", "openai/gpt-oss-20b", transport).complete([])
                self.assertIn(expected, str(raised.exception))
                self.assertNotIn("secret-provider-body", str(raised.exception))
                self.assertNotIn("dummy-key", str(raised.exception))

    def test_truncated_provider_answer_is_rejected(self) -> None:
        def transport(request, timeout):
            response = {"choices": [{"finish_reason": "length", "message": {"content": "partial"}}]}
            return io.BytesIO(json.dumps(response).encode("utf-8"))
        with self.assertRaisesRegex(GenerationError, "Längenlimit"):
            GroqClient("dummy-key", "openai/gpt-oss-20b", transport).complete([])

    def test_environment_requires_key_model_and_free_tier_confirmation(self) -> None:
        for values, expected in [
            ({}, "GROQ_API_KEY"),
            ({"GROQ_API_KEY": "dummy"}, "GROQ_MODEL"),
            ({"GROQ_API_KEY": "dummy", "GROQ_MODEL": "openai/gpt-oss-20b"}, "Free-Tarif"),
        ]:
            with self.subTest(values=values), patch.dict(os.environ, values, clear=True):
                with self.assertRaisesRegex(GenerationError, expected):
                    GroqClient.from_environment()

    def test_terminal_uses_simulated_client(self) -> None:
        client = FakeClient({"answerable": True, "answer": "`pip install requests` [S1].", "sources": ["S1"]})
        output = io.StringIO()
        with patch.object(sys, "argv", ["repo_assistant.cli", "--answer", "How do I install Requests with pip?"]), \
             patch.object(cli.GroqClient, "from_environment", return_value=client), \
             redirect_stdout(output), redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(), 0)
        self.assertIn("#L30-L39", output.getvalue())
        self.assertEqual(len(client.calls), 1)

    def test_terminal_no_hits_skips_client_and_invalid_sources_show_passages(self) -> None:
        client = FakeClient({"answerable": True, "answer": "Erfunden [S9].", "sources": ["S9"]})
        output = io.StringIO()
        with patch.object(sys, "argv", ["repo_assistant.cli", "--answer", "Kann die Bibliothek Verbindungen wiederverwenden?"]), \
             patch.object(cli.GroqClient, "from_environment", return_value=client), \
             redirect_stdout(output):
            self.assertEqual(cli.main(), 0)
        self.assertIn("kein API-Aufruf", output.getvalue())
        self.assertEqual(client.calls, [])

        output, errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["repo_assistant.cli", "--answer", "Welche Lizenz hat Requests?"]), \
             patch.object(cli.GroqClient, "from_environment", return_value=client), \
             redirect_stdout(output), redirect_stderr(errors):
            self.assertEqual(cli.main(), 1)
        self.assertIn("Quellenkennungen", errors.getvalue())
        self.assertIn("Gefundene Textstellen", output.getvalue())
        self.assertNotIn("Erfunden", output.getvalue())


if __name__ == "__main__":
    unittest.main()
