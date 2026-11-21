"""CLI ассемблера учебной виртуальной машины."""

import argparse
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import spec
from errors import CODE_OUTPUT_FILE, UvmError
from json_loader import load_program

TEST_MODE_HELP = "вывести внутреннее представление программы"


def create_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов ассемблера."""
    parser = argparse.ArgumentParser(
        prog="assembler",
        description="Ассемблер УВМ (вариант №2).",
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="JSON-файл с текстом программы",
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="файл с результатом трансляции",
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help=TEST_MODE_HELP,
    )
    return parser


def write_listing(instructions: list, path: str) -> None:
    """Записывает промежуточное представление в текстовый файл."""
    lines = [item.format_fields() for item in instructions]
    try:
        Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as error:
        raise UvmError(
            CODE_OUTPUT_FILE, f"не удалось записать {path}: {error}"
        ) from error


def main(argv=None) -> int:
    """Точка входа ассемблера."""
    args = create_parser().parse_args(argv)
    try:
        instructions = load_program(args.input)
        write_listing(instructions, args.output)
    except UvmError as error:
        print(str(error), file=sys.stderr)
        return spec.EXIT_ERROR
    print(f"Трансляция завершена: {len(instructions)} команд")
    if args.test:
        for instruction in instructions:
            print(instruction.format_fields())
    return spec.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
