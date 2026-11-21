"""Арифметико-логическое устройство учебной виртуальной машины."""

import spec


def bitreverse_32(value: int) -> int:
    """Зеркально разворачивает 32 бита беззнакового значения.

    Бит i результата равен биту 31 - i аргумента; старшие биты значения
    отбрасываются маской 0xFFFFFFFF.
    """
    source = value & spec.WORD_MASK
    result = spec.ZERO
    for _ in range(spec.WORD_BITS):
        result = (result << spec.ONE) | (source & spec.ONE)
        source >>= spec.ONE
    return result
