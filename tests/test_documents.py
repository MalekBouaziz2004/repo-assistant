"""Offline checks for Markdown splitting and source references."""

import subprocess
import sys
import tempfile
import unittest
import locale
from pathlib import Path

from repo_assistant.documents import read_document, split_markdown


ROOT = Path(__file__).resolve().parents[1]


class DocumentTests(unittest.TestCase):
    def test_introduction_headings_long_section_and_fenced_code(self) -> None:
        text = (
            "Intro text.\n\n"
            "# Start\n"
            "First paragraph.\n\n"
            "Second paragraph with enough words to need a separate chunk.\n\n"
            "```shell\n"
            "# not a heading\n"
            "echo ready\n"
            "```\n"
            "## Next\n"
            "Last line.\n"
        )
        lines = text.splitlines(keepends=True)
        chunks = split_markdown(text, "example", max_chars=65)
        self.assertEqual("".join(chunk.text for chunk in chunks), text)
        self.assertEqual(list(dict.fromkeys(chunk.heading for chunk in chunks)), ["Einleitung", "Start", "Next"])
        self.assertGreater(len([chunk for chunk in chunks if chunk.heading == "Start"]), 1)
        for chunk in chunks:
            self.assertEqual(chunk.text, "".join(lines[chunk.start_line - 1:chunk.end_line]))
        self.assertIn("# not a heading\n", "".join(chunk.text for chunk in chunks if chunk.heading == "Start"))

    def test_tilde_fence_and_hash_without_space(self) -> None:
        text = "# Title\n~~~md\n## hidden\n~~~\n#Not heading\n## Visible\n"
        chunks = split_markdown(text, "test")
        self.assertEqual([chunk.heading for chunk in chunks], ["Title", "Visible"])
        self.assertIn("#Not heading\n", chunks[0].text)

    def test_long_single_line_remains_whole(self) -> None:
        text = "# Title\n" + "x" * 80 + "\n"
        chunks = split_markdown(text, "test", max_chars=20)
        self.assertEqual("".join(chunk.text for chunk in chunks), text)
        self.assertEqual(chunks[-1].start_line, 2)
        self.assertEqual(chunks[-1].end_line, 2)

    def test_missing_and_empty_file_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.md"
            with self.assertRaisesRegex(ValueError, "Datei nicht gefunden"):
                read_document(path)
            path.write_text(" \n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Datei ist leer"):
                read_document(path)

    def test_example_readme_round_trip(self) -> None:
        path = ROOT / "data/documents/requests.README.md"
        text = read_document(path)
        chunks = split_markdown(text, "requests.README")
        self.assertGreater(len(chunks), 3)
        self.assertEqual("".join(chunk.text for chunk in chunks), text)
        lines = text.splitlines(keepends=True)
        for chunk in chunks:
            self.assertEqual(chunk.text, "".join(lines[chunk.start_line - 1:chunk.end_line]))

    def test_terminal_command(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "repo_assistant.cli", "data/documents/requests.README.md"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding=locale.getencoding(),
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Zeilen 1-", result.stdout)
        self.assertIn("Installing Requests and Supported Versions", result.stdout)


if __name__ == "__main__":
    unittest.main()
