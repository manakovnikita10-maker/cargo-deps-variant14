"""Точка входа прототипа."""

from config import parse_config


def main(argv=None):
    """Вывести значение каждой из пяти опций."""
    config = parse_config(argv)
    for key, value in vars(config).items():
        print(f"{key} = {value if value is not None else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
