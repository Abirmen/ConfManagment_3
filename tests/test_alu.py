"""Тесты операции bitreverse 32-битного АЛУ."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from alu import bitreverse_32

HIGH_BITS_VALUE = 0x1_0000_0001
VECTORS = [
    0,
    1,
    2,
    5,
    15,
    0x1FFFFF,
    0x7FFFFFFF,
    0x80000000,
    0xAAAAAAAA,
    0x55555555,
    0x12345678,
    0x0F0F0F,
    0xFFFFFFFF,
]


def reference(value: int) -> int:
    """Эталонный разворот битов через строковое представление."""
    bits = format(value & 0xFFFFFFFF, "032b")
    return int(bits[::-1], 2)


class AluTest(unittest.TestCase):
    """Проверяет математическую точность разворота битов."""

    def test_reference_vectors(self) -> None:
        """Разворот совпадает с эталоном на наборе значений."""
        for value in VECTORS:
            with self.subTest(value=value):
                self.assertEqual(bitreverse_32(value), reference(value))

    def test_method_examples(self) -> None:
        """Ключевые примеры из методички."""
        self.assertEqual(bitreverse_32(1), 0x80000000)
        self.assertEqual(bitreverse_32(15), 0xF0000000)
        self.assertEqual(bitreverse_32(5), 0xA0000000)
        self.assertEqual(bitreverse_32(0), 0)

    def test_involution(self) -> None:
        """Двойной разворот возвращает исходное значение."""
        for value in VECTORS:
            with self.subTest(value=value):
                twice = bitreverse_32(bitreverse_32(value))
                self.assertEqual(twice, value)

    def test_high_bits_ignored(self) -> None:
        """Старшие биты за пределами 32 отбрасываются."""
        self.assertEqual(
            bitreverse_32(HIGH_BITS_VALUE), bitreverse_32(1)
        )
