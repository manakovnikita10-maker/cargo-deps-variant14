"""Обратные зависимости в тестовом репозитории или графе Cargo."""

from copy import copy

from src.graph import dependency_graph, dfs, read_test_graph


def invert_graph(graph):
    """Развернуть стрелки, сохранив вершины без входящих рёбер."""
    incoming = {node: [] for node in graph}
    for package, dependencies in graph.items():
        for dependency in dependencies:
            incoming[dependency].append(package)
    return incoming


def reverse_dependencies(graph, start, exclude=""):
    """Найти все пакеты, из которых достижима указанная вершина."""
    if start not in graph:
        raise ValueError(f"пакет {start} отсутствует в заданном графе")
    incoming = invert_graph(graph)
    visited = dfs(start, incoming.__getitem__, exclude)
    return [node for node in visited if node != start]


def cargo_scope(config):
    """Собрать граф выбранного пакета Cargo для обратного поиска."""
    scope = copy(config)
    scope.package, scope.version = config.within
    scope.filter = ""
    return dependency_graph(scope)


def find_dependents(config):
    """Выбрать граф и вывести результат обратного обхода."""
    if config.test:
        graph = read_test_graph(config.repository)
        start = config.package
    else:
        graph = cargo_scope(config)
        start = f"{config.package.lower()}@{config.version.split('+', 1)[0]}"
        for node in graph:
            if node.lower().split("+", 1)[0] == start:
                start = node
                break
    return reverse_dependencies(graph, start, config.filter)
