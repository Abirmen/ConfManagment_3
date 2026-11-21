"""Сквозные тесты трёх программ тестовой задачи над вектором длины 8."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import interpreter
import spec
from encoder import encode_program
from json_loader import load_program

DATA_DIR = Path(__file__).resolve().parent
VECTOR_LENGTH = 8
INVOLUTION_DST = 400
CASES = [
    ("task_vector8_case1.json",
     [1, 2, 4, 8, 15, 16, 255, 1024], 100, 200, 33),
    ("task_vector8_case2.json",
     [0, 1, 3, 5, 170, 255, 65535, 1048575], 100, 200, 33),
    ("task_vector8_case3.json",
     [4096, 65535, 1048575, 1, 123456, 654321, 777, 2024], 60, 300, 35),
]


def reference(value: int) -> int:
    """Эталонный разворот битов через строковое представление."""
    bits = format(value, "032b")
    return int(bits[::-1], 2)


def run_program(filename: str, range_text: str) -> dict:
    """Ассемблирует и выполняет программу, возвращает дамп памяти."""
    program = load_program(str(DATA_DIR / filename))
    with tempfile.TemporaryDirectory() as folder:
        binary = Path(folder) / "program.bin"
        dump_path = Path(folder) / "dump.json"
        binary.write_bytes(encode_program(program))
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = interpreter.main(
                ["-i", str(binary), "-o", str(dump_path),
                 "-r", range_text]
            )
        if code != spec.EXIT_OK:
            raise AssertionError(err.getvalue())
        return json.loads(dump_path.read_text(encoding="utf-8"))


class TaskVectorTest(unittest.TestCase):
    """Проверяет результаты трёх вариантов тестовой задачи."""

    def test_new_vectors(self) -> None:
        """Новый вектор равен поэлементному bitreverse исходного."""
        for filename, values, source, dst, _ in CASES:
            with self.subTest(program=filename):
                end = dst + VECTOR_LENGTH - 1
                cells = run_program(filename, f"{source}:{end}")["cells"]
                for index, value in enumerate(values):
                    self.assertEqual(
                        cells[str(dst + index)], reference(value)
                    )

    def test_source_vectors_unchanged(self) -> None:
        """Исходные векторы не изменяются."""
        for filename, values, source, dst, _ in CASES:
            with self.subTest(program=filename):
                end = source + VECTOR_LENGTH - 1
                cells = run_program(filename, f"{source}:{end}")["cells"]
                for index, value in enumerate(values):
                    self.assertEqual(cells[str(source + index)], value)

    def test_involution(self) -> None:
        """Повторный bitreverse возвращает исходный элемент."""
        filename, values, source, dst, _ = CASES[-1]
        dump = run_program(filename, f"{INVOLUTION_DST}:{INVOLUTION_DST}")
        self.assertEqual(dump["cells"][str(INVOLUTION_DST)], values[0])

    def test_program_sizes(self) -> None:
        """Число выполненных команд совпадает с ожидаемым."""
        for filename, values, source, dst, commands in CASES:
            with self.subTest(program=filename):
                dump = run_program(filename, "0:0")
                self.assertEqual(
                    dump["executed_instructions"], commands
                )
