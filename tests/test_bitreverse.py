"""Сквозные тесты программы с командой bitreverse."""

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
PROGRAM = DATA_DIR / "test_bitreverse.json"
VALUES = [1, 2, 15, 0x123456, 0x0F0F0F, 0x1FFFFF]
SOURCE_START = 110
DST_START = 200
RANGE_START = 200
RANGE_END = 205
EXPECTED_COMMANDS = 25


def reference(value: int) -> int:
    """Эталонный разворот битов через строковое представление."""
    bits = format(value, "032b")
    return int(bits[::-1], 2)


class BitreverseProgramTest(unittest.TestCase):
    """Проверяет выполнение программы bitreverse на УВМ."""

    def run_program(self, folder: Path, range_text: str) -> dict:
        """Ассемблирует и выполняет программу, возвращает дамп."""
        binary = folder / "program.bin"
        dump_path = folder / "dump.json"
        binary.write_bytes(encode_program(load_program(str(PROGRAM))))
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = interpreter.main(
                ["-i", str(binary), "-o", str(dump_path),
                 "-r", range_text]
            )
        self.assertEqual(code, spec.EXIT_OK)
        self.assertEqual(err.getvalue(), "")
        return json.loads(dump_path.read_text(encoding="utf-8"))

    def test_results(self) -> None:
        """Результаты совпадают с эталонным разворотом битов."""
        with tempfile.TemporaryDirectory() as folder:
            dump = self.run_program(
                Path(folder), f"{RANGE_START}:{RANGE_END}"
            )
            cells = dump["cells"]
            for index, value in enumerate(VALUES):
                actual = cells[str(DST_START + index)]
                self.assertEqual(actual, reference(value))

    def test_source_unchanged(self) -> None:
        """Исходные значения в памяти остаются неизменными."""
        with tempfile.TemporaryDirectory() as folder:
            dump = self.run_program(Path(folder), f"100:{RANGE_END}")
            cells = dump["cells"]
            for index, value in enumerate(VALUES):
                self.assertEqual(cells[str(SOURCE_START + index)], value)

    def test_executed_commands(self) -> None:
        """Выполнены все 25 команд программы."""
        with tempfile.TemporaryDirectory() as folder:
            dump = self.run_program(Path(folder), "0:0")
            self.assertEqual(
                dump["executed_instructions"], EXPECTED_COMMANDS
            )
