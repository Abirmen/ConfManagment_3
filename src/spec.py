"""Спецификация учебной виртуальной машины (вариант №2).

Модуль содержит именованные константы и описания битовых полей всех
команд УВМ. Остальные модули обращаются только к этим именам, поэтому
в коде нет магических чисел.
"""

from dataclasses import dataclass

ZERO = 0
ONE = 1

COMMAND_BITS = 40
COMMAND_BYTES = 5
COMMAND_MASK = (ONE << COMMAND_BITS) - ONE

OPCODE_BITS = 7
OPCODE_MASK = (ONE << OPCODE_BITS) - ONE
OPCODE_LOAD_CONST = 35
OPCODE_READ_MEM = 3
OPCODE_WRITE_MEM = 122
OPCODE_BITREVERSE = 110

REGISTER_BITS = 6
REGISTER_COUNT = 64

WORD_BITS = 32
WORD_MASK = (ONE << WORD_BITS) - ONE

ADDRESS_BITS = 12
CONSTANT_BITS = 21
OFFSET_BITS = 14

DATA_MEMORY_SIZE = 65536

LOAD_CONST_CONST_SHIFT = 7
LOAD_CONST_REG_SHIFT = 28
READ_MEM_ADDR_SHIFT = 7
READ_MEM_REG_SHIFT = 19
WRITE_MEM_SRC_SHIFT = 7
WRITE_MEM_ADDR_SHIFT = 13
BITREVERSE_BASE_SHIFT = 7
BITREVERSE_DST_SHIFT = 13
BITREVERSE_OFFSET_SHIFT = 25

EXIT_OK = 0
EXIT_ERROR = 1

DEFAULT_START_ADDRESS = 0
DEFAULT_END_ADDRESS = 31


@dataclass(frozen=True)
class OperandSpec:
    """Битовое поле команды: имя, буква, разрядность и сдвиг."""

    name: str
    letter: str
    bits: int
    shift: int

    @property
    def maximum(self) -> int:
        """Максимальное допустимое значение поля."""
        return (ONE << self.bits) - ONE


@dataclass(frozen=True)
class CommandSpec:
    """Формат команды УВМ: мнемоника, код операции и поля."""

    name: str
    opcode: int
    operands: tuple

    @property
    def operand_names(self) -> tuple:
        """Имена полей команды в порядке объявления."""
        return tuple(item.name for item in self.operands)

    @property
    def used_mask(self) -> int:
        """Маска битов, занятых кодом операции и полями."""
        mask = OPCODE_MASK
        for item in self.operands:
            mask |= item.maximum << item.shift
        return mask

    def operand(self, name: str) -> OperandSpec:
        """Возвращает описание поля по имени."""
        for item in self.operands:
            if item.name == name:
                return item
        raise KeyError(name)


LOAD_CONST = CommandSpec(
    name="load_const",
    opcode=OPCODE_LOAD_CONST,
    operands=(
        OperandSpec("const", "B", CONSTANT_BITS, LOAD_CONST_CONST_SHIFT),
        OperandSpec("reg", "C", REGISTER_BITS, LOAD_CONST_REG_SHIFT),
    ),
)

READ_MEM = CommandSpec(
    name="read_mem",
    opcode=OPCODE_READ_MEM,
    operands=(
        OperandSpec("addr", "B", ADDRESS_BITS, READ_MEM_ADDR_SHIFT),
        OperandSpec("reg", "C", REGISTER_BITS, READ_MEM_REG_SHIFT),
    ),
)

WRITE_MEM = CommandSpec(
    name="write_mem",
    opcode=OPCODE_WRITE_MEM,
    operands=(
        OperandSpec("src_reg", "B", REGISTER_BITS, WRITE_MEM_SRC_SHIFT),
        OperandSpec("addr_reg", "C", REGISTER_BITS, WRITE_MEM_ADDR_SHIFT),
    ),
)

BITREVERSE = CommandSpec(
    name="bitreverse",
    opcode=OPCODE_BITREVERSE,
    operands=(
        OperandSpec(
            "base_reg", "B", REGISTER_BITS, BITREVERSE_BASE_SHIFT
        ),
        OperandSpec("dst_addr", "C", ADDRESS_BITS, BITREVERSE_DST_SHIFT),
        OperandSpec("offset", "D", OFFSET_BITS, BITREVERSE_OFFSET_SHIFT),
    ),
)

COMMANDS = (LOAD_CONST, READ_MEM, WRITE_MEM, BITREVERSE)
COMMANDS_BY_NAME = {item.name: item for item in COMMANDS}
COMMANDS_BY_OPCODE = {item.opcode: item for item in COMMANDS}
