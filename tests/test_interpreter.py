"""Тесты интерпретатора УВМ и JSON-дампа памяти."""

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
COPY_ARRAY = DATA_DIR / "copy_array.json"
COPY_VALUES = [11, 22, 33, 44, 55]
COPY_DESTINATION = 10
RANGE_TEXT = "0:19"
RANGE_START = 0
RANGE_END = 19
DEFAULT_CELLS = 32
EXPECTED_COMMANDS = 30


def assemble(source: Path, destination: Path) -> None:
    """Ассемблирует JSON-программу в двоичный файл."""
    destination.write_bytes(encode_program(load_program(str(source))))


def run_cli(arguments: list) -> tuple:
    """Запускает интерпретатор и перехватывает stdout и stderr."""
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = interpreter.main(arguments)
    return code, out.getvalue(), err.getvalue()


def read_dump(path: Path) -> dict:
    """Читает JSON-дамп памяти."""
    return json.loads(path.read_text(encoding="utf-8"))


class InterpreterTest(unittest.TestCase):
    """Проверяет выполнение программ и сохранение дампа."""

    def test_copy_array(self) -> None:
        """Копирование массива даёт совпадающие области памяти."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "copy_array.bin"
            dump_path = Path(folder) / "dump.json"
            assemble(COPY_ARRAY, binary)
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(dump_path), "-r", RANGE_TEXT]
            )
            self.assertEqual(code, spec.EXIT_OK)
            self.assertEqual(err, "")
            cells = read_dump(dump_path)["cells"]
            for index, value in enumerate(COPY_VALUES):
                self.assertEqual(cells[str(index)], value)
                target = str(index + COPY_DESTINATION)
                self.assertEqual(cells[target], value)

    def test_dump_metadata(self) -> None:
        """Дамп содержит диапазон и статистику выполнения."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "copy_array.bin"
            dump_path = Path(folder) / "dump.json"
            assemble(COPY_ARRAY, binary)
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(dump_path), "-r", RANGE_TEXT]
            )
            dump = read_dump(dump_path)
            self.assertEqual(
                dump["range"],
                {"start": RANGE_START, "end": RANGE_END},
            )
            self.assertEqual(dump["executed_instructions"], EXPECTED_COMMANDS)
            self.assertEqual(dump["program_size"], EXPECTED_COMMANDS)
            self.assertEqual(dump["memory_size"], spec.DATA_MEMORY_SIZE)
            self.assertIn(f"Выполнено команд: {EXPECTED_COMMANDS}", out)

    def test_default_range(self) -> None:
        """Без --range дамп содержит 32 ячейки."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "copy_array.bin"
            dump_path = Path(folder) / "dump.json"
            assemble(COPY_ARRAY, binary)
            run_cli(["-i", str(binary), "-o", str(dump_path)])
            self.assertEqual(
                len(read_dump(dump_path)["cells"]), DEFAULT_CELLS
            )

    def test_invalid_range(self) -> None:
        """Перевёрнутый диапазон даёт ошибку E13."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "copy_array.bin"
            assemble(COPY_ARRAY, binary)
            dump_path = Path(folder) / "dump.json"
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(dump_path), "-r", "5:4"]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn("E13", err)

    def test_bad_binary_length(self) -> None:
        """Файл длиной 3 байта отвергается с кодом E09."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "bad.bin"
            binary.write_bytes(b"\x00\x01\x02")
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(Path(folder) / "d.json")]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn("E09", err)

    def test_empty_binary(self) -> None:
        """Пустой двоичный файл даёт ошибку E09."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "empty.bin"
            binary.write_bytes(b"")
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(Path(folder) / "d.json")]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn("E09", err)

    def test_unknown_opcode(self) -> None:
        """Слово с кодом операции 0 даёт ошибку E10."""
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / "zero.bin"
            binary.write_bytes(b"\x00" * spec.COMMAND_BYTES)
            code, out, err = run_cli(
                ["-i", str(binary), "-o", str(Path(folder) / "d.json")]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn("E10", err)
