"""Опции командной строки и проверка их значений."""

import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit

INVALID_PORT = 0
DEFAULT_REPOSITORY = "https://index.crates.io/"
PACKAGE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
TEST_NAME = re.compile(r"[A-Z]")
VERSION_NUMBER = r"(?:0|[1-9][0-9]*)"
VERSION_SUFFIX = r"[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*"
VERSION_FORMAT = re.compile(
    rf"{VERSION_NUMBER}\.{VERSION_NUMBER}\.{VERSION_NUMBER}"
    rf"(?:-(?P<pre>{VERSION_SUFFIX}))?(?:\+{VERSION_SUFFIX})?"
)


def exact_version(value):
    """Принять полную версию SemVer, включая prerelease и build."""
    match = VERSION_FORMAT.fullmatch(value)
    if match:
        parts = (match["pre"] or "").split(".")
        if all(not (part.isdigit() and part.startswith("0") and part != "0")
               for part in parts):
            return value
    raise argparse.ArgumentTypeError("ожидается точная версия, например 1.0.40")


def filter_text(value):
    """Принять непустую подстроку для поиска в имени пакета."""
    if not value.strip() or any(not char.isprintable() for char in value):
        raise argparse.ArgumentTypeError("нужна непустая печатная подстрока")
    return value


def repository_url(source):
    """Проверить и нормализовать адрес sparse-индекса."""
    source = source.removeprefix("sparse+")
    if any(char.isspace() for char in source):
        raise ValueError("в URL есть пробельные символы")
    try:
        url = urlsplit(source)
        port = url.port
    except ValueError as error:
        raise ValueError("ожидается корректный HTTP(S)-адрес") from error
    if url.scheme not in {"http", "https"} or not url.hostname:
        raise ValueError("ожидается HTTP(S)-адрес с именем сервера")
    if port == INVALID_PORT:
        raise ValueError("порт должен быть больше нуля")
    if any((url.username is not None, url.password is not None,
            url.query, url.fragment)):
        raise ValueError("URL содержит учётные данные, запрос или фрагмент")
    return source.rstrip("/")


def make_parser():
    """Описать параметры программы и сообщения справки."""
    parser = argparse.ArgumentParser(description="Граф зависимостей Cargo")
    parser.add_argument("--package", required=True, help="имя пакета")
    parser.add_argument("--repository", help="URL индекса или путь к JSON")
    parser.add_argument("--test", action="store_true", help="локальный JSON")
    parser.add_argument("--version", type=exact_version, help="точная версия")
    parser.add_argument("--filter", type=filter_text, help="фильтр")
    parser.add_argument("--output-dir", type=Path, default=Path("out"),
                        help="каталог для DOT и SVG")
    parser.add_argument("--no-open", action="store_true",
                        help="сохранить SVG без запуска браузера")
    return parser


def validate_test(parser, config):
    """Проверить параметры для тестового репозитория."""
    if not TEST_NAME.fullmatch(config.package):
        parser.error("--package в режиме --test должен быть буквой A–Z")
    if config.version is not None:
        parser.error("--version используется только для индекса Cargo")
    if not config.repository or not Path(config.repository).is_file():
        parser.error("--test требует --repository с путём к файлу")


def validate_cargo(parser, config):
    """Проверить имя, точную версию и адрес индекса Cargo."""
    if not PACKAGE_NAME.fullmatch(config.package):
        parser.error("--package должен содержать буквы ASCII, цифры, - или _")
    if config.version is None:
        parser.error("для Cargo требуется --version")
    try:
        source = config.repository
        if source is None:
            source = DEFAULT_REPOSITORY
        config.repository = repository_url(source)
    except ValueError as error:
        parser.error(f"--repository: {error}")


def parse_config(argv=None):
    """Прочитать опции и проверить их совместимость."""
    parser = make_parser()
    config = parser.parse_args(argv)
    config.filter = config.filter or ""
    if config.test:
        validate_test(parser, config)
    else:
        validate_cargo(parser, config)
    return config
