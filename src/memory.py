"""Память данных и регистровый файл учебной виртуальной машины."""

import spec
from errors import CODE_MEMORY_BOUNDS, UvmError


class DataMemory:
    """Память данных: массив 32-битных беззнаковых ячеек."""

    def __init__(self, size: int = spec.DATA_MEMORY_SIZE) -> None:
        """Создаёт память заданного размера, заполненную нулями."""
        self._cells = [spec.ZERO] * size

    @property
    def size(self) -> int:
        """Количество ячеек памяти."""
        return len(self._cells)

    def check_address(self, address: int) -> None:
        """Проверяет, что адрес принадлежит памяти данных."""
        if address < spec.ZERO or address >= self.size:
            raise UvmError(
                CODE_MEMORY_BOUNDS,
                f"адрес памяти {address} вне диапазона "
                f"0..{self.size - spec.ONE}",
            )

    def read(self, address: int) -> int:
        """Читает значение ячейки памяти."""
        self.check_address(address)
        return self._cells[address]

    def write(self, address: int, value: int) -> None:
        """Записывает 32-битное значение в ячейку памяти."""
        self.check_address(address)
        self._cells[address] = value & spec.WORD_MASK

    def snapshot(self, start: int, end: int) -> dict:
        """Возвращает словарь «адрес -> значение» для диапазона."""
        self.check_address(start)
        self.check_address(end)
        return {
            str(index): self._cells[index]
            for index in range(start, end + spec.ONE)
        }


class RegisterFile:
    """Банк из 64 регистров УВМ."""

    def __init__(self) -> None:
        """Создаёт регистры, инициализированные нулями."""
        self._values = [spec.ZERO] * spec.REGISTER_COUNT

    def check_index(self, index: int) -> None:
        """Проверяет корректность номера регистра."""
        if index < spec.ZERO or index >= spec.REGISTER_COUNT:
            raise UvmError(
                CODE_MEMORY_BOUNDS,
                f"номер регистра {index} вне диапазона "
                f"0..{spec.REGISTER_COUNT - spec.ONE}",
            )

    def read(self, index: int) -> int:
        """Читает значение регистра."""
        self.check_index(index)
        return self._values[index]

    def write(self, index: int, value: int) -> None:
        """Записывает значение в регистр."""
        self.check_index(index)
        self._values[index] = value & spec.WORD_MASK

    def snapshot(self) -> dict:
        """Возвращает словарь «номер регистра -> значение»."""
        return {
            str(index): value
            for index, value in enumerate(self._values)
        }
