"""Декодирование 5-байтовых машинных слов в промежуточное представление."""

import spec
from errors import (
    CODE_BINARY_LENGTH,
    CODE_UNKNOWN_OPCODE,
    CODE_UNUSED_BITS,
    UvmError,
)
from instruction import Instruction


def split_words(data: bytes) -> list:
    """Разбивает байтовый поток на 40-битные машинные слова."""
    size = len(data)
    if size % spec.COMMAND_BYTES != spec.ZERO:
        raise UvmError(
            CODE_BINARY_LENGTH,
            f"размер {size} байт не кратен {spec.COMMAND_BYTES} байтам",
        )
    offsets = range(spec.ZERO, size, spec.COMMAND_BYTES)
    return [
        int.from_bytes(
            data[offset:offset + spec.COMMAND_BYTES], "little"
        )
        for offset in offsets
    ]


def decode_word(word: int) -> Instruction:
    """Декодирует одно 40-битное слово в инструкцию IR."""
    opcode = word & spec.OPCODE_MASK
    command = spec.COMMANDS_BY_OPCODE.get(opcode)
    if command is None:
        raise UvmError(
            CODE_UNKNOWN_OPCODE, f"неизвестный код операции A={opcode}"
        )
    extra = word & (spec.COMMAND_MASK & ~command.used_mask)
    if extra != spec.ZERO:
        raise UvmError(
            CODE_UNUSED_BITS,
            f"ненулевые неиспользуемые биты: 0x{extra:X}",
        )
    values = {
        operand.name: (word >> operand.shift) & operand.maximum
        for operand in command.operands
    }
    return Instruction.create(command, values)


def decode_program(data: bytes) -> list:
    """Декодирует байтовый поток в список инструкций."""
    return [decode_word(word) for word in split_words(data)]
