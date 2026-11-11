"""Сравнение версий и ограничений SemVer из индекса Cargo."""

import re

from src.config import VERSION_NUMBER, VERSION_SUFFIX

RELEASE_PARTS = 3
COMPARATOR = re.compile(
    rf"(?P<op>\^|~|>=|<=|>|<|=)?\s*"
    rf"(?P<major>{VERSION_NUMBER})"
    rf"(?:\.(?P<minor>{VERSION_NUMBER}|[xX*]))?"
    rf"(?:\.(?P<patch>{VERSION_NUMBER}|[xX*]))?"
    rf"(?:-(?P<pre>{VERSION_SUFFIX}))?(?:\+{VERSION_SUFFIX})?"
)


def version_key(version):
    """Преобразовать полную версию в ключ сортировки по правилам SemVer."""
    release, _, prerelease = version.split("+", 1)[0].partition("-")
    numbers = tuple(int(part) for part in release.split("."))
    parts = tuple((0, int(part)) if part.isdigit() else (1, part)
                  for part in prerelease.split(".") if part)
    return numbers, not prerelease, parts


def requirement_parts(requirement):
    """Разобрать одно ограничение Cargo."""
    match = COMPARATOR.fullmatch(requirement.strip())
    if not match:
        raise ValueError(f"неподдерживаемое ограничение Cargo: {requirement}")
    parts = [part for part in match.group("major", "minor", "patch") if part]
    numbers = tuple(int(part) for part in parts if part.isdigit())
    wildcard = len(numbers) < len(parts)
    width = len(numbers)
    operator = match["op"] or "^"
    if wildcard:
        operator = "="
    floor = numbers + (0,) * (RELEASE_PARTS - width)
    value = ".".join(str(number) for number in floor)
    if match["pre"]:
        value = f"{value}-{match['pre']}"
    return operator, width, version_key(value)


def comparison_value(version, width):
    """Для неполной версии сравнить только указанные компоненты."""
    if width < RELEASE_PARTS:
        return version[0][:width]
    return version


def matches(version, condition):
    """Проверить кандидата для одного сравнения, caret или tilde."""
    operator, width, floor = condition
    if operator in {"^", "~"}:
        limit = min(width - 1, 1)
        if operator == "^":
            limit = next((i for i, part in enumerate(floor[0][:width]) if part),
                         width - 1)
        prefix = limit + 1
        return version >= floor and version[0][:prefix] == floor[0][:prefix]

    left = comparison_value(version, width)
    right = comparison_value(floor, width)
    if operator == "=":
        return left == right
    if operator == ">":
        return left > right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    return left <= right


def parse_requirement(requirement):
    """Разобрать список ограничений, разделённых запятыми."""
    if requirement.strip() in {"*", "x", "X"}:
        return []
    return [requirement_parts(part) for part in requirement.split(",")]


def select_release(records, requirement):
    """Найти наибольшую подходящую неотозванную версию."""
    conditions = parse_requirement(requirement)
    prereleases = {floor[0] for _, _, floor in conditions if not floor[1]}
    candidates = []
    for entry in records:
        if entry.get("yanked", False):
            continue
        value = version_key(entry["vers"])
        if not value[1] and value[0] not in prereleases:
            continue
        if all(matches(value, condition) for condition in conditions):
            candidates.append((value, entry["vers"]))
    if not candidates:
        raise ValueError(f"нет доступной версии для {requirement!r}")
    return max(candidates)[1]
