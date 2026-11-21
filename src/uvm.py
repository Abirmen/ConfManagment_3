"""Модель учебной виртуальной машины и цикл интерпретации."""

import spec
from decoder import decode_program
from errors import CODE_BINARY_LENGTH, CODE_UNKNOWN_OPCODE, UvmError
from instruction import Instruction
from memory import DataMemory, RegisterFile


class ProgramMemory:
    """Память команд УВМ, загружаемая из двоичного файла."""

    def __init__(self, data: bytes) -> None:
        """Декодирует байтовый поток в память команд."""
        self._commands = decode_program(data)
        if len(self._commands) < spec.ONE:
            raise UvmError(CODE_BINARY_LENGTH, "программа не содержит команд")

    def __len__(self) -> int:
        """Количество команд в памяти команд."""
        return len(self._commands)

    def __getitem__(self, index: int) -> Instruction:
        """Возвращает команду по адресу в памяти команд."""
        return self._commands[index]


class VirtualMachine:
    """Интерпретатор УВМ с раздельными памятью команд и данных."""

    def __init__(self, program: ProgramMemory, data=None,
                 registers=None) -> None:
        """Создаёт машину с заданной памятью команд."""
        self.program = program
        self.data = data if data is not None else DataMemory()
        self.registers = (
            registers if registers is not None else RegisterFile()
        )
        self._pc = spec.ZERO
        self.executed = spec.ZERO
        self._handlers = {
            spec.OPCODE_LOAD_CONST: self._load_const,
            spec.OPCODE_READ_MEM: self._read_mem,
            spec.OPCODE_WRITE_MEM: self._write_mem,
        }

    @property
    def program_counter(self) -> int:
        """Текущий счётчик команд."""
        return self._pc

    def run(self) -> int:
        """Выполняет программу до конца и возвращает число команд."""
        while self._pc < len(self.program):
            self.step()
        return self.executed

    def step(self) -> None:
        """Выполняет одну команду и сдвигает счётчик команд."""
        instruction = self.program[self._pc]
        handler = self._handlers.get(instruction.opcode)
        if handler is None:
            raise UvmError(
                CODE_UNKNOWN_OPCODE,
                f"нет обработчика для команды {instruction.name}",
            )
        handler(instruction)
        self._pc += spec.ONE
        self.executed += spec.ONE

    def _load_const(self, instruction: Instruction) -> None:
        """Выполняет load_const: regs[C] = B."""
        self.registers.write(
            instruction.value("reg"), instruction.value("const")
        )

    def _read_mem(self, instruction: Instruction) -> None:
        """Выполняет read_mem: regs[C] = data_mem[B]."""
        value = self.data.read(instruction.value("addr"))
        self.registers.write(instruction.value("reg"), value)

    def _write_mem(self, instruction: Instruction) -> None:
        """Выполняет write_mem: data_mem[regs[C]] = regs[B]."""
        address = self.registers.read(instruction.value("addr_reg"))
        value = self.registers.read(instruction.value("src_reg"))
        self.data.write(address, value)
