"""Тесты загрузки и валидации JSON-программ."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import spec
from errors import UvmError
from json_loader import load_program

DATA_DIR = Path(__file__).resolve().parent
SPEC_TESTS = DATA_DIR / "spec_tests.json"


def load_reference_program() -> list:
    """Загружает эталонную программу из спецификации."""
    return load_program(str(SPEC_TESTS))


class JsonLoaderTest(unittest.TestCase):
    """Проверяет разбор корректных программ и коды ошибок."""

    def test_all_commands_loaded(self) -> None:
        """Все четыре команды спецификации разобраны по порядку."""
        program = load_reference_program()
        names = [item.name for item in program]
        self.assertEqual(
            names,
            ["load_const", "read_mem", "write_mem", "bitreverse"],
        )

    def test_field_values(self) -> None:
        """Значения полей совпадают со спецификацией."""
        program = load_reference_program()
        first = program[0]
        self.assertEqual(first.opcode, spec.OPCODE_LOAD_CONST)
        self.assertEqual(first.value("const"), 557)
        self.assertEqual(first.value("reg"), 45)

    def test_format_fields(self) -> None:
        """Формат IR совпадает с контрольными строками методички."""
        program = load_reference_program()
        lines = [item.format_fields() for item in program]
        self.assertEqual(
            lines,
            [
                "A=35, B=557, C=45",
                "A=3, B=623, C=34",
                "A=122, B=23, C=29",
                "A=110, B=53, C=639, D=905",
            ],
        )

    def test_unknown_command(self) -> None:
        """Неизвестная мнемоника приводит к ошибке E05."""
        self.assert_error({"op": "nop"}, "E05")

    def test_missing_field(self) -> None:
        """Отсутствующее поле приводит к ошибке E06."""
        self.assert_error({"op": "load_const", "reg": 1}, "E06")

    def test_extra_field(self) -> None:
        """Лишнее поле приводит к ошибке E04."""
        self.assert_error(
            {"op": "load_const", "const": 1, "reg": 1, "x": 2}, "E04"
        )

    def test_out_of_range(self) -> None:
        """Выход за битовый диапазон приводит к ошибке E08."""
        self.assert_error(
            {"op": "load_const", "const": 2097152, "reg": 1}, "E08"
        )

    def test_register_range(self) -> None:
        """Номер регистра 64 недопустим."""
        self.assert_error(
            {"op": "load_const", "const": 1, "reg": 64}, "E08"
        )

    def test_wrong_type(self) -> None:
        """Строка вместо числа приводит к ошибке E07."""
        self.assert_error(
            {"op": "load_const", "const": "1", "reg": 1}, "E07"
        )

    def test_boolean_rejected(self) -> None:
        """Логическое значение не считается целым числом."""
        self.assert_error(
            {"op": "load_const", "const": True, "reg": 1}, "E07"
        )

    def test_invalid_json(self) -> None:
        """Синтаксическая ошибка JSON даёт код E03."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{", encoding="utf-8")
            self.assert_error_file(path, "E03")

    def test_missing_file(self) -> None:
        """Несуществующий файл даёт код E02."""
        path = Path(tempfile.gettempdir()) / "no_such_uvm_program.json"
        self.assert_error_file(path, "E02")

    def test_empty_program(self) -> None:
        """Пустой массив команд недопустим."""
        self.assert_error_document({"program": []}, "E04")

    def assert_error(self, command: dict, code: str) -> None:
        """Проверяет код ошибки для одной команды."""
        self.assert_error_document({"program": [command]}, code)

    def assert_error_document(self, document: dict, code: str) -> None:
        """Записывает документ во временный файл и ждёт ошибку."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "program.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assert_error_file(path, code)

    def assert_error_file(self, path: Path, code: str) -> None:
        """Проверяет, что загрузка файла даёт ожидаемый код."""
        with self.assertRaises(UvmError) as context:
            load_program(str(path))
        self.assertEqual(context.exception.code, code)
