"""Тесты памяти данных и регистрового файла УВМ."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import spec
from errors import CODE_MEMORY_BOUNDS, UvmError
from memory import DataMemory, RegisterFile

SMALL_SIZE = 4
BAD_ADDRESS = 4
TEST_VALUE = 0x1_0000_0001
MASKED_VALUE = 1


def error_code(function, *args) -> str:
    """Возвращает код ошибки, которую вызывает функция."""
    try:
        function(*args)
    except UvmError as error:
        return error.code
    return ""


def make_memory() -> DataMemory:
    """Создаёт небольшую память данных для тестов."""
    return DataMemory(SMALL_SIZE)


def make_registers() -> RegisterFile:
    """Создаёт регистровый файл для тестов."""
    return RegisterFile()


class DataMemoryTest(unittest.TestCase):
    """Проверяет чтение, запись и границы памяти данных."""

    def test_zero_initialized(self) -> None:
        """Новая память заполнена нулями."""
        memory = make_memory()
        values = [memory.read(address) for address in range(SMALL_SIZE)]
        self.assertEqual(values, [spec.ZERO] * SMALL_SIZE)

    def test_write_and_read(self) -> None:
        """Записанное значение читается по тому же адресу."""
        memory = make_memory()
        memory.write(1, 123)
        self.assertEqual(memory.read(1), 123)

    def test_value_is_masked(self) -> None:
        """Значение приводится к 32-битному беззнаковому виду."""
        memory = make_memory()
        memory.write(2, TEST_VALUE)
        self.assertEqual(memory.read(2), MASKED_VALUE)

    def test_snapshot(self) -> None:
        """Дамп диапазона содержит адреса и значения."""
        memory = make_memory()
        memory.write(1, 7)
        self.assertEqual(memory.snapshot(0, 1), {"0": 0, "1": 7})

    def test_out_of_bounds(self) -> None:
        """Адрес за пределами памяти даёт ошибку E11."""
        memory = make_memory()
        code = error_code(memory.read, BAD_ADDRESS)
        self.assertEqual(code, CODE_MEMORY_BOUNDS)

    def test_large_memory_size(self) -> None:
        """Память по умолчанию вмещает 65536 ячеек."""
        memory = DataMemory()
        self.assertEqual(memory.size, spec.DATA_MEMORY_SIZE)


class RegisterFileTest(unittest.TestCase):
    """Проверяет регистровый файл УВМ."""

    def test_zero_initialized(self) -> None:
        """Все регистры инициализированы нулями."""
        registers = make_registers()
        values = [registers.read(index) for index in range(4)]
        self.assertEqual(values, [spec.ZERO] * 4)

    def test_write_and_read(self) -> None:
        """Записанное значение читается из регистра."""
        registers = make_registers()
        registers.write(5, 42)
        self.assertEqual(registers.read(5), 42)

    def test_out_of_bounds(self) -> None:
        """Регистр с номером 64 недопустим."""
        registers = make_registers()
        code = error_code(registers.read, spec.REGISTER_COUNT)
        self.assertEqual(code, CODE_MEMORY_BOUNDS)

    def test_snapshot_size(self) -> None:
        """Дамп содержит все 64 регистра."""
        registers = make_registers()
        self.assertEqual(len(registers.snapshot()), spec.REGISTER_COUNT)
