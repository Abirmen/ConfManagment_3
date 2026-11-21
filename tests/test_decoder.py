"""Тесты декодирования машинного кода УВМ."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import spec
from decoder import decode_program, decode_word, split_words
from encoder import encode_instruction, encode_program
from errors import (
    CODE_BINARY_LENGTH,
    CODE_UNKNOWN_OPCODE,
    CODE_UNUSED_BITS,
    UvmError,
)
from json_loader import load_program

DATA_DIR = Path(__file__).resolve().parent
SPEC_TESTS = DATA_DIR / "spec_tests.json"
UNUSED_BIT = 1 << (spec.COMMAND_BITS - spec.ONE)


def load_reference_program() -> list:
    """Загружает эталонную программу из спецификации."""
    return load_program(str(SPEC_TESTS))


class DecoderTest(unittest.TestCase):
    """Проверяет обратимость кодирования и контроль ошибок."""

    def test_roundtrip(self) -> None:
        """Кодирование и декодирование не меняют команды."""
        program = load_reference_program()
        for instruction in program:
            chunk = encode_instruction(instruction)
            word = int.from_bytes(chunk, "little")
            self.assertEqual(decode_word(word), instruction)

    def test_split_words(self) -> None:
        """20 байт делятся на четыре слова."""
        program = load_reference_program()
        words = split_words(encode_program(program))
        self.assertEqual(len(words), len(program))

    def test_bad_length(self) -> None:
        """Длина, не кратная 5 байтам, даёт ошибку E09."""
        with self.assertRaises(UvmError) as context:
            decode_program(b"\x00\x01\x02")
        self.assertEqual(context.exception.code, CODE_BINARY_LENGTH)

    def test_unknown_opcode(self) -> None:
        """Код операции 0 не существует."""
        with self.assertRaises(UvmError) as context:
            decode_word(spec.ZERO)
        self.assertEqual(context.exception.code, CODE_UNKNOWN_OPCODE)

    def test_unused_bits(self) -> None:
        """Ненулевой неиспользуемый бит даёт ошибку E14."""
        program = load_reference_program()
        chunk = encode_instruction(program[0])
        word = int.from_bytes(chunk, "little") | UNUSED_BIT
        with self.assertRaises(UvmError) as context:
            decode_word(word)
        self.assertEqual(context.exception.code, CODE_UNUSED_BITS)
