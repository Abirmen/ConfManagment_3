"""Промежуточное представление (IR) команд учебной виртуальной машины."""

from dataclasses import dataclass

from spec import CommandSpec


@dataclass(frozen=True)
class Instruction:
    """Команда УВМ в промежуточном представлении."""

    command: CommandSpec
    values: tuple

    @classmethod
    def create(cls, command: CommandSpec, values: dict) -> "Instruction":
        """Создаёт команду из словаря «имя поля -> значение»."""
        ordered = tuple(values[item.name] for item in command.operands)
        return cls(command=command, values=ordered)

    @property
    def name(self) -> str:
        """Мнемоника команды."""
        return self.command.name

    @property
    def opcode(self) -> int:
        """Код операции A."""
        return self.command.opcode

    def value(self, name: str) -> int:
        """Возвращает значение поля по имени."""
        for operand, value in zip(self.command.operands, self.values):
            if operand.name == name:
                return value
        raise KeyError(name)

    def pairs(self) -> tuple:
        """Пары «описание поля, значение» в порядке полей команды."""
        return tuple(zip(self.command.operands, self.values))

    def format_fields(self) -> str:
        """Строка вида «A=35, B=557, C=45»."""
        parts = [f"A={self.opcode}"]
        for operand, value in self.pairs():
            parts.append(f"{operand.letter}={value}")
        return ", ".join(parts)

    def format_asm(self) -> str:
        """Запись команды в стиле ассемблера: имя и поля."""
        parts = [
            f"{operand.name}={value}" for operand, value in self.pairs()
        ]
        return f"{self.name} " + ", ".join(parts)

    def __str__(self) -> str:
        """Строковое представление команды."""
        return self.format_asm()
