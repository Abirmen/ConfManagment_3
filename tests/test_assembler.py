"""Тесты командной строки ассемблера."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import assembler
import spec
from errors import CODE_JSON_SYNTAX

DATA_DIR = Path(__file__).resolve().parent
SPEC_TESTS = DATA_DIR / "spec_tests.json"
EXPECTED_FIELDS = [
    "A=35, B=557, C=45",
    "A=3, B=623, C=34",
    "A=122, B=23, C=29",
    "A=110, B=53, C=639, D=905",
]


class AssemblerTest(unittest.TestCase):
    """Проверяет режим тестирования и запись результата."""

    def run_cli(self, arguments: list) -> tuple:
        """Запускает main и перехватывает stdout и stderr."""
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = assembler.main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_test_mode_prints_fields(self) -> None:
        """Режим --test печатает поля всех команд."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "program.ir.txt"
            code, out, err = self.run_cli(
                ["-i", str(SPEC_TESTS), "-o", str(output), "-t"]
            )
            self.assertEqual(code, spec.EXIT_OK)
            self.assertEqual(err, "")
            for line in EXPECTED_FIELDS:
                self.assertIn(line, out)

    def test_listing_content(self) -> None:
        """Выходной файл содержит строки внутреннего представления."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "program.ir.txt"
            self.run_cli(["-i", str(SPEC_TESTS), "-o", str(output)])
            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines, EXPECTED_FIELDS)

    def test_invalid_program_exit_code(self) -> None:
        """Ошибка разбора даёт код возврата 1 и сообщение в stderr."""
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.json"
            source.write_text("{", encoding="utf-8")
            output = Path(folder) / "result.txt"
            code, out, err = self.run_cli(
                ["-i", str(source), "-o", str(output)]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn(CODE_JSON_SYNTAX, err)
            self.assertEqual(out, "")
