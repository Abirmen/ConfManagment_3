"""Коды ошибок приложения и класс исключения.

Все сообщения выводятся в поток stderr в формате «Ошибка E08: ...»,
а код возврата процесса равен 1.
"""

CODE_USAGE = "E01"
CODE_INPUT_FILE = "E02"
CODE_JSON_SYNTAX = "E03"
CODE_SCHEMA = "E04"
CODE_UNKNOWN_OP = "E05"
CODE_MISSING_FIELD = "E06"
CODE_FIELD_TYPE = "E07"
CODE_FIELD_RANGE = "E08"
CODE_BINARY_LENGTH = "E09"
CODE_UNKNOWN_OPCODE = "E10"
CODE_MEMORY_BOUNDS = "E11"
CODE_OUTPUT_FILE = "E12"
CODE_RANGE = "E13"
CODE_UNUSED_BITS = "E14"


class UvmError(Exception):
    """Ошибка приложения с машиночитаемым кодом."""

    def __init__(self, code: str, message: str) -> None:
        """Создаёт ошибку с кодом и текстовым пояснением."""
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self) -> str:
        """Возвращает строку вида «Ошибка E08: пояснение»."""
        return f"Ошибка {self.code}: {self.message}"
