"""Тестовый индекс и рекурсивный обход графа зависимостей."""

import json
from pathlib import Path

from src.cargo_index import CargoIndex
from src.config import TEST_NAME


def read_test_graph(filename):
    """Прочитать JSON с именами из одной заглавной латинской буквы."""
    with Path(filename).open(encoding="utf-8") as stream:
        graph = json.load(stream)
    if not isinstance(graph, dict):
        raise ValueError("тестовый репозиторий должен быть объектом JSON")
    for name, neighbors in graph.items():
        if not TEST_NAME.fullmatch(name) or not isinstance(neighbors, list):
            raise ValueError(f"ожидается запись вида \"A\": [\"B\"]: {name!r}")
        for neighbor in neighbors:
            if not isinstance(neighbor, str) or neighbor not in graph:
                raise ValueError(f"{name}: неизвестный пакет {neighbor!r}")
    return graph


def dfs(start, neighbors, exclude=""):
    """Рекурсивно построить граф, посещая каждую вершину один раз."""
    graph = {}
    exclude = exclude.casefold()

    def visit(node):
        """Пометить вершину до обхода её соседей, сохраняя рёбра циклов."""
        if node in graph:
            return
        graph[node] = []
        for neighbor in dict.fromkeys(neighbors(node)):
            name = neighbor.split("@", 1)[0]
            if exclude and exclude in name.casefold():
                continue
            graph[node].append(neighbor)
            visit(neighbor)

    visit(start)
    return graph


def dependency_graph(config):
    """Построить граф по индексу Cargo или по тестовому файлу."""
    if config.test:
        graph = read_test_graph(config.repository)
        if config.package not in graph:
            raise ValueError(f"пакет {config.package} отсутствует в файле")
        return dfs(config.package, graph.__getitem__, config.filter)

    index = CargoIndex(config.repository)
    root = index.release(config.package, config.version)
    start = f"{root['name']}@{root['vers']}"
    return dfs(start, index.graph_neighbors(config.filter), config.filter)
