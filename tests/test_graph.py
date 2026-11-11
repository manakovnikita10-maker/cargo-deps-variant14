"""Проверки обхода тестового графа."""

import unittest

from src.graph import dfs, read_test_graph
from test_config import ROOT, launch


class GraphTests(unittest.TestCase):
    """Проверить циклы, исключения и несвязанные вершины."""

    def test_cycle_and_shared_dependency(self):
        """Сохранить рёбра цикла и обработать общую вершину один раз."""
        source = read_test_graph(ROOT / "tests" / "graph.json")
        graph = dfs("A", source.__getitem__)
        self.assertEqual(list(graph), ["A", "B", "D", "C", "E"])
        self.assertEqual(graph["D"], ["B"])
        self.assertEqual(graph["C"], ["D", "E"])

    def test_filter_prunes_unreachable_nodes(self):
        """Скрыть вершину с совпадением и её уникальное поддерево."""
        source = read_test_graph(ROOT / "tests" / "graph.json")
        self.assertEqual(dfs("A", source.__getitem__, "c"),
                         {"A": ["B"], "B": ["D"], "D": ["B"]})
        self.assertEqual(dfs("F", source.__getitem__), {"F": []})

    def test_missing_package(self):
        """Отобразить ошибку, если стартовой вершины нет в JSON."""
        result = launch("--test", "--repository", "tests/graph.json",
                        "--package", "Z")
        self.assertEqual(result.returncode, 1)
        self.assertIn("пакет Z отсутствует", result.stderr)
