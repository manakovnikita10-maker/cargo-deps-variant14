"""Точка входа для просмотра прямых зависимостей."""

import sys

from src.cargo_index import CargoIndex
from src.config import parse_config


def main(argv=None):
    """Найти версию в индексе и вывести объявления её зависимостей."""
    config = parse_config(argv)
    try:
        if config.test:
            raise ValueError("чтение тестового графа доступно с этапа 3")
        index = CargoIndex(config.repository)
        dependencies = index.dependencies(config.package, config.version)
    except (ValueError, KeyError, TypeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    if not dependencies:
        print("Прямых зависимостей нет.")
    for dep in dependencies:
        flags = ", optional" if dep.optional else ""
        target = f", {dep.target}" if dep.target else ""
        print(f"{dep.name} {dep.requirement} [{dep.kind}{flags}{target}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
