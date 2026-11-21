"""CLI интерпретатора учебной виртуальной машины."""

import argparse
import json
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import spec
from errors import (
    CODE_INPUT_FILE,
    CODE_OUTPUT_FILE,
    CODE_RANGE,
    UvmError,
)
from uvm import ProgramMemory, VirtualMachine

RANGE_SEPARATOR = ":"
RANGE_PARTS = 2
DEFAULT_RANGE = f"{spec.DEFAULT_START_ADDRESS}:{spec.DEFAULT_END_ADDRESS}"


def create_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов интерпретатора."""
    parser = argparse.ArgumentParser(
        prog="interpreter",
        description="Интерпретатор УВМ (вариант №2).",
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="двоичный файл с машинным кодом программы",
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="JSON-файл для дампа памяти данных",
    )
    parser.add_argument(
        "-r", "--range", default=DEFAULT_RANGE, dest="memory_range",
        help="диапазон дампа в формате START:END",
    )
    return parser


def parse_range(text: str) -> tuple:
    """Разбирает диапазон адресов вида START:END."""
    parts = text.split(RANGE_SEPARATOR)
    if len(parts) != RANGE_PARTS:
        raise UvmError(
            CODE_RANGE, f"диапазон {text!r} должен иметь вид START:END"
        )
    try:
        start = int(parts[spec.ZERO], 10)
        end = int(parts[spec.ONE], 10)
    except ValueError as error:
        raise UvmError(
            CODE_RANGE, f"нецелое число в диапазоне {text!r}"
        ) from error
    if start < spec.ZERO or end < start or end >= spec.DATA_MEMORY_SIZE:
        raise UvmError(CODE_RANGE, f"некорректный диапазон {text!r}")
    return start, end


def read_binary(path: str) -> bytes:
    """Читает двоичный файл с машинным кодом."""
    try:
        return Path(path).read_bytes()
    except OSError as error:
        raise UvmError(
            CODE_INPUT_FILE, f"не удалось прочитать {path}: {error}"
        ) from error


def build_dump(machine: VirtualMachine, start: int, end: int) -> dict:
    """Формирует структуру JSON-дампа памяти данных."""
    return {
        "range": {"start": start, "end": end},
        "memory_size": machine.data.size,
        "program_size": len(machine.program),
        "executed_instructions": machine.executed,
        "cells": machine.data.snapshot(start, end),
    }


def write_dump(dump: dict, path: str) -> None:
    """Записывает дамп памяти в JSON-файл."""
    text = json.dumps(dump, ensure_ascii=False, indent=2)
    try:
        Path(path).write_text(text + "\n", encoding="utf-8")
    except OSError as error:
        raise UvmError(
            CODE_OUTPUT_FILE, f"не удалось записать {path}: {error}"
        ) from error


def main(argv=None) -> int:
    """Точка входа интерпретатора."""
    args = create_parser().parse_args(argv)
    try:
        start, end = parse_range(args.memory_range)
        program = ProgramMemory(read_binary(args.input))
        machine = VirtualMachine(program)
        machine.run()
        dump = build_dump(machine, start, end)
        write_dump(dump, args.output)
    except UvmError as error:
        print(str(error), file=sys.stderr)
        return spec.EXIT_ERROR
    print(f"Выполнено команд: {machine.executed}")
    print(f"Дамп памяти сохранён: {args.output} ({start}:{end})")
    return spec.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
