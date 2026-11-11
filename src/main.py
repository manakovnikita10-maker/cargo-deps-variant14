"""Точка входа для построения графа зависимостей."""

import sys

from src.config import parse_config
from src.graph import dependency_graph


def main(argv=None):
    """Построить граф с помощью DFS и вывести списки смежности."""
    config = parse_config(argv)
    try:
        graph = dependency_graph(config)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    for package, dependencies in graph.items():
        print(f"{package} -> {', '.join(dependencies) or '—'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
