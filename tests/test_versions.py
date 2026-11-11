"""Проверки выбора версий Cargo."""

import unittest

from src.versions import select_release


class VersionsTests(unittest.TestCase):
    """Ограничения SemVer, предварительные и отозванные версии."""

    def test_selects_highest_matching_release(self):
        """Учитывать числовой порядок, диапазоны и yanked."""
        records = [{"vers": version} for version in
                   ("0.0.3", "0.0.4", "0.1.1", "0.1.10", "0.2.0", "1.0.0")]
        records.append({"vers": "0.1.11", "yanked": True})
        for requirement, expected in {
            "^0.1.1": "0.1.10", "^0.0.3": "0.0.3", "0.1.*": "0.1.10",
            "~0.1": "0.1.10", ">0.0, <0.2": "0.1.10", "=0.1.1": "0.1.1",
        }.items():
            with self.subTest(requirement=requirement):
                self.assertEqual(select_release(records, requirement), expected)

    def test_limits_prereleases_to_matching_version(self):
        """Разрешить prerelease только для явно запрошенного выпуска."""
        records = [{"vers": version} for version in
                   ("1.0.0-alpha", "1.0.0-beta.2", "1.0.0-beta.10",
                    "1.0.1-beta", "0.9.0")]
        self.assertEqual(select_release(records, "^1.0.0-alpha"),
                         "1.0.0-beta.10")
        self.assertEqual(select_release(records, "*"), "0.9.0")
