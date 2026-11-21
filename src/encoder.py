"""Кодирование команд УВМ в 5-байтовые машинные слова."""

import spec
from instruction import Instruction


def encode_instruction(instruction: Instruction) -> bytes:
    """Кодирует одну команду в 5 байт в порядке little-endian."""
    word = instruction.opcode
    for operand, value in instruction.pairs():
        word |= value << operand.shift
    return word.to_bytes(spec.COMMAND_BYTES, "little")


def encode_program(instructions: list) -> bytes:
    """Кодирует программу в непрерывный байтовый поток."""
    return b"".join(encode_instruction(item) for item in instructions)
