"""
Тесты для финансового трекера.
"""

import unittest
import os
import json
from fintracker.models import Category, Expense
from fintracker.storage import Storage
from fintracker.report import ReportGenerator


class TestModelsSimple(unittest.TestCase):
    """Тесты моделей."""

    def test_category_basic(self):
        """Базовый тест категории."""
        cat = Category(1, "Еда")
        self.assertEqual(cat.name, "Еда")
        self.assertEqual(cat.to_dict(), {"id": 1, "name": "Еда"})

        cat2 = Category.from_dict({"id": 2, "name": "Транспорт"})
        self.assertEqual(cat2.name, "Транспорт")

    def test_expense_basic(self):
        """Базовый тест расхода."""
        expense = Expense(1, 2, 100.0, "Обед", "2024-01-15")
        self.assertEqual(expense.amount, 100.0)
        self.assertEqual(expense.description, "Обед")

        expense_dict = expense.to_dict()
        self.assertEqual(expense_dict["amount"], 100.0)


class TestStorageSimple(unittest.TestCase):
    """Тесты хранилища."""

    def setUp(self):
        """Используем реальный тестовый файл."""
        self.test_file = "test_data.json"
        # Удаляем старый тестовый файл если есть
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def tearDown(self):
        """Очистка после теста."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def test_storage_creation(self):
        """Тест создания хранилища."""
        storage = Storage(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

        # Проверяем, что файл содержит правильную структуру
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('expenses', data)
            self.assertIn('categories', data)
            self.assertIn('next_id', data)

    def test_add_and_get_expense(self):
        """Тест добавления и получения расхода."""
        storage = Storage(self.test_file)

        # Добавляем расход
        result = storage.add_expense(1, 250.0, "Продукты")
        self.assertTrue(result)

        # Получаем расходы
        expenses = storage.get_expenses()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].amount, 250.0)
        self.assertEqual(expenses[0].description, "Продукты")

    def test_get_categories(self):
        """Тест получения категорий."""
        storage = Storage(self.test_file)
        categories = storage.get_categories()

        # Должно быть 6 начальных категорий
        self.assertEqual(len(categories), 6)

        # Проверяем названия категорий
        category_names = [cat.name for cat in categories]
        expected_names = ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Одежда", "Здоровье"]
        for name in expected_names:
            self.assertIn(name, category_names)


class TestReportSimple(unittest.TestCase):
    """Тесты отчетов."""

    def setUp(self):
        self.test_file = "test_report_data.json"
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def test_empty_report(self):
        """Тест пустого отчета."""
        storage = Storage(self.test_file)
        reporter = ReportGenerator(storage)

        report = reporter.generate_category_report("all")
        self.assertEqual(report['total_expenses'], 0)
        self.assertEqual(len(report['categories']), 0)

    def test_simple_report(self):
        """Тест простого отчета."""
        storage = Storage(self.test_file)
        reporter = ReportGenerator(storage)

        # Добавляем данные
        storage.add_expense(1, 100.0, "Продукты")  # Еда
        storage.add_expense(2, 50.0, "Метро")      # Транспорт

        report = reporter.generate_category_report("all")

        # Проверяем общую сумму
        self.assertEqual(report['total_expenses'], 150.0)

        # Должно быть 2 категории с расходами
        self.assertEqual(len(report['categories']), 2)


class TestIntegrationSimple(unittest.TestCase):
    """Интеграционные тесты."""

    def setUp(self):
        self.test_file = "test_integration_data.json"
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    def test_basic_workflow(self):
        """Тест базового рабочего процесса."""
        # 1. Создаем хранилище
        storage = Storage(self.test_file)

        # 2. Добавляем расходы
        storage.add_expense(1, 100.0, "Завтрак")
        storage.add_expense(1, 200.0, "Обед")
        storage.add_expense(2, 50.0, "Метро")

        # 3. Проверяем данные
        expenses = storage.get_expenses("all")
        self.assertEqual(len(expenses), 3)

        # 4. Генерируем отчет
        reporter = ReportGenerator(storage)
        report = reporter.generate_category_report("all")
        self.assertEqual(report['total_expenses'], 350.0)

        # 5. Удаляем один расход
        storage.delete_expense(1)
        expenses_after = storage.get_expenses("all")
        self.assertEqual(len(expenses_after), 2)


if __name__ == '__main__':
    print("Запуск простых тестов...")
    unittest.main(verbosity=2)