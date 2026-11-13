"""Проверки представления DOT и отрисовки SVG."""

import shutil
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

from src.visualization import dot_source
from test_config import launch

SVG_NS = {"svg": "http://www.w3.org/2000/svg"}


class VisualizationTests(unittest.TestCase):
    """Проверить сериализацию графа и сценарий запуска."""

    def test_dot_contains_cycles_and_single_nodes(self):
        """Сохранить двустороннюю связь и явно объявить отдельный узел."""
        sample = {"A": ["B"], "B": ["A"], "C": []}
        output = dot_source(sample)
        for line in ('"A" -> "B";', '"B" -> "A";', '"C";'):
            with self.subTest(line=line):
                self.assertIn(line, output)

    @unittest.skipUnless(shutil.which("dot"), "Graphviz не установлен")
    def test_cli_renders_a_valid_svg(self):
        """Проверить файлы DOT и SVG после запуска программы."""
        with tempfile.TemporaryDirectory() as directory:
            result = launch("--test", "--repository", "tests/graph.json",
                            "--package", "A", "--no-open",
                            "--output-dir", directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = Path(directory)
            self.assertIn('"D" -> "B";',
                          (output / "A.dot").read_text(encoding="utf-8"))
            svg = ElementTree.parse(output / "A.svg")
            labels = {node.text for node in svg.findall(".//svg:text", SVG_NS)}
            self.assertEqual(labels, set("ABCDE"))
