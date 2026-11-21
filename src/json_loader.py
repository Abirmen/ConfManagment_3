"""Загрузка и валидация JSON-программ на языке ассемблера УВМ."""

import json
from pathlib import Path

import spec
from errors import (
    CODE_FIELD_RANGE,
    CODE_FIELD_TYPE,
    CODE_INPUT_FILE,
    CODE_JSON_SYNTAX,
    CODE_MISSING_FIELD,
    CODE_SCHEMA,
    CODE_UNKNOWN_OP,
    UvmError,
)
from instruction import Instruction

PROGRAM_KEY = "program"
OPCODE_KEY = "op"
COMMENT_KEY = "comment"


def read_json(path: str) -> object:
    """Читает JSON-файл и возвращает разобранный объект."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise UvmError(
            CODE_INPUT_FILE, f"не удалось прочитать {path}: {error}"
        ) from error
    try:
        return json.loads(text)
    except ValueError as error:
        raise UvmError(
            CODE_JSON_SYNTAX, f"некорректный JSON в {path}: {error}"
        ) from error


def extract_commands(document: object) -> list:
    """Проверяет документ верхнего уровня и возвращает список команд."""
    if not isinstance(document, dict):
        raise UvmError(CODE_SCHEMA, "корневой элемент должен быть объектом")
    extra = set(document) - {PROGRAM_KEY}
    if extra:
        names = ", ".join(sorted(extra))
        raise UvmError(CODE_SCHEMA, f"неизвестные ключи: {names}")
    if PROGRAM_KEY not in document:
        raise UvmError(CODE_MISSING_FIELD, "отсутствует ключ program")
    commands = document[PROGRAM_KEY]
    if not isinstance(commands, list):
        raise UvmError(CODE_FIELD_TYPE, "program должен быть массивом")
    if len(commands) < spec.ONE:
        raise UvmError(CODE_SCHEMA, "program не должен быть пустым")
    return commands


def check_keys(item: dict, command: spec.CommandSpec, where: str) -> None:
    """Проверяет наличие обязательных и отсутствие лишних полей."""
    allowed = set(command.operand_names) | {OPCODE_KEY, COMMENT_KEY}
    extra = set(item) - allowed
    if extra:
        names = ", ".join(sorted(extra))
        raise UvmError(CODE_SCHEMA, f"{where}: лишние поля: {names}")
    missing = set(command.operand_names) - set(item)
    if missing:
        names = ", ".join(sorted(missing))
        raise UvmError(CODE_MISSING_FIELD, f"{where}: нет полей: {names}")


def parse_value(item: dict, operand: spec.OperandSpec, where: str) -> int:
    """Извлекает и проверяет значение одного поля команды."""
    value = item[operand.name]
    if isinstance(value, bool) or not isinstance(value, int):
        raise UvmError(
            CODE_FIELD_TYPE,
            f"{where}: поле {operand.name} должно быть целым числом",
        )
    if value < spec.ZERO or value > operand.maximum:
        raise UvmError(
            CODE_FIELD_RANGE,
            f"{where}: поле {operand.name}={value} вне диапазона "
            f"0..{operand.maximum}",
        )
    return value


def parse_command(item: object, index: int) -> Instruction:
    """Разбирает одну команду JSON и возвращает инструкцию IR."""
    where = f"команда №{index + spec.ONE}"
    if not isinstance(item, dict):
        raise UvmError(CODE_FIELD_TYPE, f"{where}: ожидается объект")
    if OPCODE_KEY not in item:
        raise UvmError(CODE_MISSING_FIELD, f"{where}: отсутствует поле op")
    name = item[OPCODE_KEY]
    if not isinstance(name, str):
        raise UvmError(
            CODE_FIELD_TYPE, f"{where}: поле op должно быть строкой"
        )
    command = spec.COMMANDS_BY_NAME.get(name)
    if command is None:
        raise UvmError(
            CODE_UNKNOWN_OP, f"{where}: неизвестная команда {name!r}"
        )
    check_keys(item, command, where)
    values = {
        operand.name: parse_value(item, operand, where)
        for operand in command.operands
    }
    return Instruction.create(command, values)


def load_program(path: str) -> list:
    """Загружает JSON-программу и возвращает список инструкций IR."""
    document = read_json(path)
    commands = extract_commands(document)
    return [
        parse_command(item, index)
        for index, item in enumerate(commands)
    ]
