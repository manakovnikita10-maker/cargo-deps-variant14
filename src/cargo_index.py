"""Чтение JSON Lines напрямую из HTTP-индекса Cargo."""

import json
from dataclasses import dataclass
from http import HTTPStatus
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.config import PACKAGE_NAME

HTTP_TIMEOUT = 12
NAME_GROUP_LENGTH = 3


@dataclass(frozen=True)
class Dependency:
    """Одна запись о прямой зависимости в индексе."""

    name: str
    requirement: str
    kind: str
    optional: bool
    target: str | None
    registry: str | None

    @classmethod
    def from_record(cls, entry):
        """Учесть настоящее имя пакета для переименованных зависимостей."""
        return cls(entry.get("package") or entry["name"], entry["req"],
                   entry.get("kind") or "normal",
                   entry.get("optional", False), entry.get("target"),
                   entry.get("registry"))


def index_path(name):
    """Найти относительный путь файла пакета по правилам Cargo."""
    if not PACKAGE_NAME.fullmatch(name):
        raise ValueError(f"недопустимое имя пакета: {name!r}")
    name = name.lower()
    length = len(name)
    if length < NAME_GROUP_LENGTH:
        return f"{length}/{name}"
    if length == NAME_GROUP_LENGTH:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


def download_records(url, name):
    """Получить записи версий одного пакета и обработать ошибки HTTP."""
    request = Request(url, headers={"User-Agent": "cargo-deps-variant14/1.0"})
    try:
        with urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return [json.loads(line) for line in response if line.strip()]
    except HTTPError as error:
        if error.code == HTTPStatus.NOT_FOUND:
            raise ValueError(f"пакет {name} отсутствует в индексе") from error
        raise ValueError(f"HTTP {error.code} при чтении {name}") from error
    except (URLError, OSError) as error:
        raise ValueError(f"индекс недоступен для {name}: {error}") from error
    except (ValueError, UnicodeError) as error:
        raise ValueError(f"некорректный JSON в индексе для {name}") from error


class CargoIndex:
    """Индекс с кешем записей, действующим до завершения программы."""

    def __init__(self, url):
        """Запомнить адрес и создать кеш записей."""
        self.url = url.rstrip("/")
        self.records = {}

    def releases(self, name):
        """Получить все опубликованные версии пакета."""
        key = name.lower()
        if key not in self.records:
            url = f"{self.url}/{index_path(name)}"
            self.records[key] = download_records(url, name)
        return self.records[key]

    def release(self, name, version):
        """Найти запись точной версии, даже если она отозвана."""
        for entry in self.releases(name):
            if entry["vers"].split("+", 1)[0] == version.split("+", 1)[0]:
                return entry
        raise ValueError(f"в индексе нет версии {name}@{version}")

    def dependencies(self, name, version):
        """Прочитать все объявленные прямые зависимости точной версии."""
        entry = self.release(name, version)
        return [Dependency.from_record(dep) for dep in entry["deps"]]
