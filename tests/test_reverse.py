"""Проверки обратного обхода."""

import unittest

from src.graph import read_test_graph
from src.reverse import reverse_dependencies
from test_config import ROOT, launch


class ReverseTests(unittest.TestCase):
    """Обратные связи для развилки, цикла и изолированной вершины."""

    def test_walks_incoming_edges(self):
        """Граф из D включает пакеты с прямой или транзитивной связью."""
        graph = read_test_graph(ROOT / "tests" / "graph.json")
        self.assertEqual(reverse_dependencies(graph, "D"), ["B", "A", "C", "G"])
        self.assertEqual(reverse_dependencies(graph, "D", "C"), ["B", "A"])
        self.assertEqual(reverse_dependencies(graph, "F"), ["G"])

    def test_reverse_cli(self):
        """Проверить режим на пакете без обратных зависимостей."""
        result = launch("--test", "--repository", "tests/graph.json",
                        "--package", "G", "--reverse")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Обратных зависимостей нет.")
