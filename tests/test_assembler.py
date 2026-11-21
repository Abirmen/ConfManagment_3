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
EXPECTED_SIZE = 20
EXPECTED_BYTES = [
    "0xA3, 0x16, 0x01, 0xD0, 0x02",
    "0x83, 0x37, 0x11, 0x01, 0x00",
    "0xFA, 0xAB, 0x03, 0x00, 0x00",
    "0xEE, 0xFA, 0x4F, 0x12, 0x07",
]
EXPECTED_FILE = bytes.fromhex(
    "A31601D0028337110100FAAB030000EEFA4F1207"
)


class AssemblerTest(unittest.TestCase):
    """Проверяет режим тестирования и запись машинного кода."""

    def run_cli(self, arguments: list) -> tuple:
        """Запускает main и перехватывает stdout и stderr."""
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            code = assembler.main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_test_mode_prints_bytes(self) -> None:
        """Режим --test печатает по 5 байт на команду."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "program.bin"
            code, out, err = self.run_cli(
                ["-i", str(SPEC_TESTS), "-o", str(output), "-t"]
            )
            self.assertEqual(code, spec.EXIT_OK)
            self.assertEqual(err, "")
            for line in EXPECTED_BYTES:
                self.assertIn(line, out)

    def test_binary_file_content(self) -> None:
        """Двоичный файл содержит 20 байт контрольной программы."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "program.bin"
            self.run_cli(["-i", str(SPEC_TESTS), "-o", str(output)])
            data = output.read_bytes()
            self.assertEqual(len(data), EXPECTED_SIZE)
            self.assertEqual(data, EXPECTED_FILE)

    def test_file_size_message(self) -> None:
        """Ассемблер сообщает размер созданного файла."""
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "program.bin"
            code, out, err = self.run_cli(
                ["-i", str(SPEC_TESTS), "-o", str(output)]
            )
            message = f"Размер двоичного файла: {EXPECTED_SIZE} байт"
            self.assertEqual(code, spec.EXIT_OK)
            self.assertIn(message, out)

    def test_invalid_program_exit_code(self) -> None:
        """Ошибка разбора даёт код возврата 1 и сообщение в stderr."""
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.json"
            source.write_text("{", encoding="utf-8")
            output = Path(folder) / "result.bin"
            code, out, err = self.run_cli(
                ["-i", str(source), "-o", str(output)]
            )
            self.assertEqual(code, spec.EXIT_ERROR)
            self.assertIn(CODE_JSON_SYNTAX, err)
            self.assertEqual(out, "")
