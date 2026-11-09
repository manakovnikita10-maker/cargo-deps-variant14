"""Проверки параметров консольного прототипа."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "src" / "main.py"
ARGS = ["--package", "quote", "--version", "1.0.40"]


def launch(*args):
    """Запустить программу и получить её вывод."""
    return subprocess.run(
        [sys.executable, str(PROGRAM), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


class ConfigTests(unittest.TestCase):
    """Успешный запуск и ошибки во всех пяти настройках."""

    def test_accepts_options(self):
        """Проверить валидные имя, версию, URL и фильтр."""
        result = launch(*ARGS, "--repository", "https://index.crates.io",
                        "--filter", "ident")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "package = quote", "repository = https://index.crates.io",
            "test = False", "version = 1.0.40", "filter = ident",
        ])

    def test_accepts_local_mode(self):
        """Проверить запуск в режиме локального репозитория."""
        result = launch("--test", "--package", "A",
                        "--repository", "tests/graph.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_invalid_options(self):
        """Проверить ошибки для каждого параметра."""
        invalid = {
            "--package": ["--package", "../quote", "--version", "1.0.40"],
            "--version": ["--package", "quote", "--version", "1.0"],
            "--repository": [*ARGS, "--repository", "not-an-url"],
            "--test": ["--test", "--package", "A"],
            "--filter": [*ARGS, "--filter", " "],
        }
        for option, args in invalid.items():
            with self.subTest(option=option):
                result = launch(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn(option, result.stderr.splitlines()[-1])


if __name__ == "__main__":
    unittest.main()
