"""Правила автоматического аудита оформления репозитория.

Модуль реализует проверки из перечня нарушений оформления git-репозитория:
размер файлов и строк, длина и число параметров функций, цикломатическая
сложность, docstrings, отсутствие комментариев, числовые литералы
в сравнениях и соответствие имён PEP 8.
"""

import ast
import io
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_LINES = 1000
MAX_LINE_LENGTH = 79
MAX_FUNCTION_LINES = 40
MAX_ARGUMENTS = 7
MAX_COMPLEXITY = 10
MAX_SCRIPT_LINE_LENGTH = 120
SCRIPT_GLOBS = (
    "run.sh",
    "tests/*.json",
    "tests/*.ps1",
)

SNAKE_CASE = re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
UPPER_CASE = re.compile(r"^[A-Z][A-Z0-9_]*$")

BRANCH_NODES = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.ExceptHandler,
    ast.With,
    ast.IfExp,
)
COMPREHENSION_NODES = (
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
DOCSTRING_NODES = (
    ast.Module,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
)
@dataclass(frozen=True)
class Violation:
    """Нарушение правила оформления."""

    rule: str
    path: str
    line: int
    message: str

    def format(self) -> str:
        """Строка для вывода в отчёте теста."""
        return f"{self.rule} {self.path}:{self.line}: {self.message}"


def make_violation(rule: str, path: Path, line: int,
                   message: str) -> Violation:
    """Создаёт объект нарушения."""
    return Violation(rule, str(path), line, message)


def check_lines(path: Path, text: str) -> list:
    """Проверяет размер файла и длину каждой строки."""
    violations = []
    lines = text.splitlines()
    if len(lines) > MAX_FILE_LINES:
        message = f"файл содержит {len(lines)} строк"
        violations.append(make_violation("Р1", path, 1, message))
    for number, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_LENGTH:
            message = f"длина строки {len(line)} больше {MAX_LINE_LENGTH}"
            violations.append(make_violation("Р2", path, number, message))
    return violations


def check_comments(path: Path, text: str) -> list:
    """Ищет комментарии в Python-файле."""
    violations = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                violations.append(
                    make_violation("К1", path, token.start[0], "комментарий")
                )
    except tokenize.TokenError:
        return violations
    return violations


def check_docstrings(path: Path, tree: ast.Module) -> list:
    """Проверяет наличие docstrings у модулей, классов и функций."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, DOCSTRING_NODES):
            if ast.get_docstring(node) is None:
                name = getattr(node, "name", "<модуль>")
                message = f"нет docstring: {name}"
                violations.append(
                    make_violation("К1", path, node.lineno, message)
                )
    return violations


def count_arguments(arguments: ast.arguments) -> int:
    """Считает все параметры функции, включая vararg и kwarg."""
    names = (
        arguments.posonlyargs
        + arguments.args
        + arguments.kwonlyargs
    )
    total = len(names)
    if arguments.vararg is not None:
        total += 1
    if arguments.kwarg is not None:
        total += 1
    return total


def calculate_complexity(node: ast.AST) -> int:
    """Считает цикломатическую сложность по ветвлениям."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, BRANCH_NODES):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, COMPREHENSION_NODES):
            complexity += 1
    return complexity


def check_function(path: Path, node: ast.AST) -> list:
    """Проверяет длину, параметры и сложность функции."""
    violations = []
    length = node.end_lineno - node.lineno + 1
    if length > MAX_FUNCTION_LINES:
        message = f"функция {node.name} занимает {length} строк"
        violations.append(
            make_violation("Ф1", path, node.lineno, message)
        )
    count = count_arguments(node.args)
    if count > MAX_ARGUMENTS:
        message = f"у функции {node.name} {count} параметров"
        violations.append(
            make_violation("А1", path, node.lineno, message)
        )
    complexity = calculate_complexity(node)
    if complexity > MAX_COMPLEXITY:
        message = f"сложность {node.name} равна {complexity}"
        violations.append(
            make_violation("Ц1", path, node.lineno, message)
        )
    return violations


def is_numeric(node: ast.AST) -> bool:
    """Определяет числовой литерал, в том числе со знаком минус."""
    if isinstance(node, ast.Constant):
        number = isinstance(node.value, (int, float))
        return number and not isinstance(node.value, bool)
    if isinstance(node, ast.UnaryOp):
        return is_numeric(node.operand)
    return False


def check_compare_literals(path: Path, tree: ast.Module) -> list:
    """Ищет числовые литералы внутри сравнений."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left] + list(node.comparators)
            for operand in operands:
                if is_numeric(operand):
                    message = "числовой литерал в сравнении"
                    violations.append(
                        make_violation("М1", path, node.lineno, message)
                    )
    return violations


def check_module_name(path: Path) -> list:
    """Проверяет имя модуля."""
    if SNAKE_CASE.match(path.stem):
        return []
    message = f"имя модуля {path.stem} не в snake_case"
    return [make_violation("И1", path, 1, message)]


def check_class_names(path: Path, tree: ast.Module) -> list:
    """Проверяет имена классов."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not PASCAL_CASE.match(node.name):
                message = f"имя класса {node.name} не в PascalCase"
                violations.append(
                    make_violation("И1", path, node.lineno, message)
                )
    return violations


def check_function_names(path: Path, tree: ast.Module) -> list:
    """Проверяет имена функций и методов."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODES):
            allowed = SNAKE_CASE.match(node.name)
            if not allowed:
                message = f"имя функции {node.name} не в snake_case"
                violations.append(
                    make_violation("И1", path, node.lineno, message)
                )
    return violations


def check_variable_names(path: Path, tree: ast.Module) -> list:
    """Проверяет имена переменных, констант и параметров."""
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if not is_valid_name(node.id):
                message = f"имя {node.id} не по PEP 8"
                violations.append(
                    make_violation("И1", path, node.lineno, message)
                )
        if isinstance(node, ast.arg):
            if not is_valid_name(node.arg):
                message = f"параметр {node.arg} не по PEP 8"
                violations.append(
                    make_violation("И1", path, node.lineno, message)
                )
    return violations


def is_valid_name(name: str) -> bool:
    """Проверяет, что имя в snake_case или UPPER_SNAKE_CASE."""
    return bool(SNAKE_CASE.match(name) or UPPER_CASE.match(name))


def audit_file(path: Path) -> list:
    """Выполняет все проверки одного файла."""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    violations = check_lines(path, text)
    violations += check_comments(path, text)
    violations += check_docstrings(path, tree)
    violations += check_compare_literals(path, tree)
    violations += check_module_name(path)
    violations += check_class_names(path, tree)
    violations += check_function_names(path, tree)
    violations += check_variable_names(path, tree)
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODES):
            violations += check_function(path, node)
    return violations


def iter_script_files(root: Path) -> list:
    """Возвращает скрипты запуска и файлы примеров."""
    files = []
    for pattern in SCRIPT_GLOBS:
        if "*" in pattern:
            files += sorted(root.glob(pattern))
        else:
            files.append(root / pattern)
    return [path for path in files if path.exists()]


def audit_script(path: Path) -> list:
    """Проверяет размер файла и длину строк скрипта."""
    violations = []
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if len(lines) > MAX_FILE_LINES:
        message = f"файл содержит {len(lines)} строк"
        violations.append(make_violation("Р1", path, 1, message))
    for number, line in enumerate(lines, 1):
        if len(line) > MAX_SCRIPT_LINE_LENGTH:
            message = (
                f"длина строки {len(line)} больше "
                f"{MAX_SCRIPT_LINE_LENGTH}"
            )
            violations.append(
                make_violation("Р6", path, number, message)
            )
    return violations


def iter_python_files(root: Path) -> list:
    """Возвращает все Python-файлы каталогов src и tests."""
    files = sorted(root.glob("src/*.py"))
    files += sorted(root.glob("tests/*.py"))
    return files


def audit_repository(root: Path) -> list:
    """Проверяет Python-файлы, скрипты запуска и данные."""
    violations = []
    for path in iter_python_files(root):
        violations += audit_file(path)
    for path in iter_script_files(root):
        violations += audit_script(path)
    return violations
