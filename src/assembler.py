"""CLI ассемблера учебной виртуальной машины."""

import argparse
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import spec
from encoder import encode_instruction, encode_program
from errors import CODE_OUTPUT_FILE, UvmError
from json_loader import load_program

TEST_MODE_HELP = "вывести машинный код в байтовом виде"


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
        help="двоичный файл с машинным кодом",
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help=TEST_MODE_HELP,
    )
    return parser


def format_bytes(chunk: bytes) -> str:
    """Форматирует байты в виде «0xA3, 0x16, ...»."""
    return ", ".join(f"0x{byte:02X}" for byte in chunk)


def write_binary(path: str, data: bytes) -> None:
    """Записывает машинный код в двоичный файл."""
    try:
        Path(path).write_bytes(data)
    except OSError as error:
        raise UvmError(
            CODE_OUTPUT_FILE, f"не удалось записать {path}: {error}"
        ) from error


def main(argv=None) -> int:
    """Точка входа ассемблера."""
    args = create_parser().parse_args(argv)
    try:
        instructions = load_program(args.input)
        binary = encode_program(instructions)
        write_binary(args.output, binary)
    except UvmError as error:
        print(str(error), file=sys.stderr)
        return spec.EXIT_ERROR
    print(f"Размер двоичного файла: {len(binary)} байт")
    if args.test:
        for instruction in instructions:
            print(format_bytes(encode_instruction(instruction)))
    return spec.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
