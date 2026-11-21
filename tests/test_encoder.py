"""Тесты кодирования команд УВМ в машинный код."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import spec
from encoder import encode_instruction, encode_program
from json_loader import load_program

DATA_DIR = Path(__file__).resolve().parent
SPEC_TESTS = DATA_DIR / "spec_tests.json"
EXPECTED_PROGRAM_SIZE = 20
EXPECTED_HEX = [
    "A31601D002",
    "8337110100",
    "FAAB030000",
    "EEFA4F1207",
]


def load_reference_program() -> list:
    """Загружает эталонную программу из спецификации."""
    return load_program(str(SPEC_TESTS))


class EncoderTest(unittest.TestCase):
    """Проверяет побайтовое кодирование четырёх команд."""

    def test_control_vectors(self) -> None:
        """Байты совпадают с контрольными значениями методички."""
        program = load_reference_program()
        encoded = [
            encode_instruction(item).hex().upper()
            for item in program
        ]
        self.assertEqual(encoded, EXPECTED_HEX)

    def test_instruction_size(self) -> None:
        """Каждая команда занимает ровно 5 байт."""
        program = load_reference_program()
        sizes = [len(encode_instruction(item)) for item in program]
        self.assertEqual(
            sizes, [spec.COMMAND_BYTES] * len(program)
        )

    def test_program_size(self) -> None:
        """Размер программы равен 20 байтам."""
        program = load_reference_program()
        binary = encode_program(program)
        self.assertEqual(len(binary), EXPECTED_PROGRAM_SIZE)
