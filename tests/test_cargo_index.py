"""Проверки преобразования путей и выбора записи версии Cargo."""

import unittest
from unittest.mock import patch

from src.cargo_index import CargoIndex, index_path


class CargoIndexTests(unittest.TestCase):
    """Тесты на фиксированных записях индекса."""

    def test_index_paths(self):
        """Проверить все четыре варианта пути в sparse-индексе."""
        for name, path in {"X": "1/x", "ab": "2/ab",
                           "syn": "3/s/syn", "quote": "qu/ot/quote"}.items():
            with self.subTest(name=name):
                self.assertEqual(index_path(name), path)

    @patch("src.cargo_index.download_records")
    def test_uses_exact_release(self, download):
        """Выбрать зависимости точной версии и учесть переименование."""
        download.return_value = [
            {"vers": "1.0.0", "deps": [
                {"name": "macro", "package": "proc-macro2", "req": "^1",
                 "kind": "normal", "optional": True}
            ]},
            {"vers": "2.0.0", "deps": []},
        ]
        index = CargoIndex("https://index.crates.io")
        dep, = index.dependencies("quote", "1.0.0")
        self.assertEqual((dep.name, dep.requirement), ("proc-macro2", "^1"))
        self.assertTrue(dep.optional)
        self.assertEqual(index.dependencies("quote", "2.0.0"), [])
        download.assert_called_once_with("https://index.crates.io/qu/ot/quote",
                                         "quote")
        with self.assertRaisesRegex(ValueError, "quote@3.0.0"):
            index.dependencies("quote", "3.0.0")
