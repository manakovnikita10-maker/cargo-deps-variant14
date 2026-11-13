"""Точка входа для визуализации графа зависимостей."""

import sys

from src.config import parse_config
from src.graph import dependency_graph
from src.visualization import render_graph, show_image


def main(argv=None):
    """Построить граф, сохранить DOT и SVG и показать изображение."""
    config = parse_config(argv)
    try:
        graph = dependency_graph(config)
        name = config.package
        if config.version:
            name = f"{name}@{config.version}"
        dot_file, svg_file = render_graph(graph, config.output_dir, name)
        print(f"DOT: {dot_file}")
        print(f"SVG: {svg_file}")
        if not config.no_open:
            show_image(svg_file)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
