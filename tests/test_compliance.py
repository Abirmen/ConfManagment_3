"""Тест автоматического аудита оформления репозитория."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TESTS_DIR.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import audit_rules


class ComplianceTest(unittest.TestCase):
    """Проверяет соблюдение правил оформления кода."""

    def test_python_style(self) -> None:
        """Все Python-файлы проходят аудит без нарушений."""
        violations = audit_rules.audit_repository(ROOT_DIR)
        report = "\n".join(item.format() for item in violations)
        self.assertEqual(violations, [], report)

    def test_required_files(self) -> None:
        """В корне присутствуют обязательные файлы и каталоги."""
        required = [
            "README.md",
            ".gitignore",
            "run.sh",
            "src",
            "tests",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((ROOT_DIR / name).exists())
