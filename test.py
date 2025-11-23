"""
Полные тесты для финансового трекера с БД.
"""

import unittest
import os
import json
import csv
import tempfile
import sqlite3
from fintracker.models import Category, Expense
from fintracker.database import Database
from fintracker.storage import Storage
from fintracker.report import ReportGenerator
from fintracker.command import CommandHandler


class TestCategory(unittest.TestCase):
    """Тесты для класса Category."""

    def test_category_creation(self):
        """Тест создания категории с корректными параметрами."""
        category = Category(1, "Еда")
        self.assertEqual(category.id, 1)
        self.assertEqual(category.name, "Еда")

    def test_to_dict(self):
        """Тест преобразования категории в словарь."""
        category = Category(1, "Транспорт")
        expected_dict = {'id': 1, 'name': 'Транспорт'}
        self.assertEqual(category.to_dict(), expected_dict)

    def test_from_dict(self):
        """Тест создания категории из словаря."""
        data = {'id': 2, 'name': 'Развлечения'}
        category = Category.from_dict(data)
        self.assertEqual(category.id, 2)
        self.assertEqual(category.name, 'Развлечения')

    def test_from_dict_invalid_data(self):
        """Тест создания категории из некорректных данных."""
        with self.assertRaises(KeyError):
            Category.from_dict({'name': 'Без ID'})
        with self.assertRaises(KeyError):
            Category.from_dict({'id': 1})


class TestExpense(unittest.TestCase):
    """Тесты для класса Expense."""

    def test_expense_creation(self):
        """Тест создания расхода с корректными параметрами."""
        expense = Expense(1, 2, 100.50, "Обед", "2024-01-15")
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.category_id, 2)
        self.assertEqual(expense.amount, 100.50)
        self.assertEqual(expense.description, "Обед")
        self.assertEqual(expense.date, "2024-01-15")

    def test_to_dict(self):
        """Тест преобразования расхода в словарь."""
        expense = Expense(1, 2, 100.50, "Обед", "2024-01-15")
        expected_dict = {
            'id': 1,
            'category_id': 2,
            'amount': 100.50,
            'description': 'Обед',
            'date': '2024-01-15'
        }
        self.assertEqual(expense.to_dict(), expected_dict)

    def test_from_dict(self):
        """Тест создания расхода из словаря."""
        data = {
            'id': 1,
            'category_id': 2,
            'amount': 100.50,
            'description': 'Обед',
            'date': '2024-01-15'
        }
        expense = Expense.from_dict(data)
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.amount, 100.50)

    def test_from_dict_missing_fields(self):
        """Тест создания расхода из словаря с отсутствующими полями."""
        with self.assertRaises(KeyError):
            Expense.from_dict({'id': 1, 'amount': 100})


class TestDatabase(unittest.TestCase):
    """Тесты для класса Database."""

    def setUp(self):
        """Создаем тестовую базу данных."""
        self.test_db = "test_finance.db"
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
        self.db = Database(self.test_db)

    def tearDown(self):
        """Удаляем тестовую базу данных."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)

    def test_database_creation(self):
        """Тест создания базы данных и таблиц."""
        self.assertTrue(os.path.exists(self.test_db))

        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn('categories', tables)
            self.assertIn('expenses', tables)

    def test_initial_categories(self):
        """Тест начальных категорий."""
        categories = self.db.get_categories()
        self.assertEqual(len(categories), 6)

        expected_names = ["Еда", "Транспорт", "Развлечения", "Коммунальные", "Одежда", "Здоровье"]
        actual_names = [cat.name for cat in categories]

        for expected_name in expected_names:
            self.assertIn(expected_name, actual_names)

    def test_add_expense_success(self):
        """Тест успешного добавления расхода."""
        result = self.db.add_expense(1, 100.0, "Продукты")
        self.assertTrue(result)

        expenses = self.db.get_expenses()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].description, "Продукты")

    def test_add_expense_with_date(self):
        """Тест добавления расхода с указанной датой."""
        result = self.db.add_expense(2, 200.0, "Такси", "2024-01-15")
        self.assertTrue(result)

        expenses = self.db.get_expenses()
        self.assertEqual(expenses[0].date, "2024-01-15")

    def test_get_expenses_periods(self):
        """Тест получения расходов за разные периоды."""
        self.db.add_expense(1, 100.0, "Расход 1")
        self.db.add_expense(2, 200.0, "Расход 2")

        all_expenses = self.db.get_expenses("all")
        self.assertEqual(len(all_expenses), 2)

        month_expenses = self.db.get_expenses("month")
        self.assertEqual(len(month_expenses), 2)

    def test_delete_existing_expense(self):
        """Тест удаления существующего расхода."""
        self.db.add_expense(1, 100.0, "Для удаления")
        expenses_before = self.db.get_expenses()

        result = self.db.delete_expense(1)
        self.assertTrue(result)

        expenses_after = self.db.get_expenses()
        self.assertEqual(len(expenses_after), len(expenses_before) - 1)

    def test_delete_nonexistent_expense(self):
        """Тест удаления несуществующего расхода."""
        result = self.db.delete_expense(999)
        self.assertFalse(result)

    def test_get_category_stats(self):
        """Тест получения статистики по категориям."""
        self.db.add_expense(1, 100.0, "Еда 1")
        self.db.add_expense(1, 200.0, "Еда 2")
        self.db.add_expense(2, 150.0, "Транспорт")

        stats = self.db.get_category_stats("all")
        self.assertEqual(len(stats), 2)

        food_stats = next(stat for stat in stats if stat['category_name'] == 'Еда')
        self.assertEqual(food_stats['total_amount'], 300.0)
        self.assertEqual(food_stats['transaction_count'], 2)


class TestStorage(unittest.TestCase):
    """Тесты для класса Storage."""

    def setUp(self):
        """Создаем тестовое хранилище."""
        self.test_db = "test_storage.db"
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
        self.storage = Storage(self.test_db)

    def tearDown(self):
        """Удаляем тестовую базу данных."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)

    def test_storage_initialization(self):
        """Тест инициализации хранилища."""
        self.assertEqual(self.storage.database.db_path, self.test_db)
        self.assertTrue(os.path.exists(self.test_db))

    def test_add_expense(self):
        """Тест добавления расхода через хранилище."""
        result = self.storage.add_expense(1, 250.0, "Продукты")
        self.assertTrue(result)

        expenses = self.storage.get_expenses()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].description, "Продукты")

    def test_get_categories(self):
        """Тест получения категорий через хранилище."""
        categories = self.storage.get_categories()
        self.assertEqual(len(categories), 6)
        self.assertIn("Еда", [cat.name for cat in categories])

    def test_get_expenses_different_periods(self):
        """Тест получения расходов за разные периоды."""
        self.storage.add_expense(1, 100.0, "Завтрак")
        self.storage.add_expense(2, 200.0, "Такси")

        all_expenses = self.storage.get_expenses("all")
        self.assertEqual(len(all_expenses), 2)

        month_expenses = self.storage.get_expenses("month")
        self.assertEqual(len(month_expenses), 2)

    def test_delete_expense(self):
        """Тест удаления расхода через хранилище."""
        self.storage.add_expense(1, 100.0, "Для удаления")
        result = self.storage.delete_expense(1)
        self.assertTrue(result)

        expenses = self.storage.get_expenses()
        self.assertEqual(len(expenses), 0)

    def test_delete_nonexistent_expense(self):
        """Тест удаления несуществующего расхода."""
        result = self.storage.delete_expense(999)
        self.assertFalse(result)


class TestReportGenerator(unittest.TestCase):
    """Тесты для класса ReportGenerator."""

    def setUp(self):
        """Создаем тестовое хранилище и генератор отчетов."""
        self.test_db = "test_report.db"
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
        self.storage = Storage(self.test_db)
        self.reporter = ReportGenerator(self.storage)

    def tearDown(self):
        """Удаляем тестовую базу данных."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)

    def test_empty_report(self):
        """Тест генерации отчета без данных."""
        report = self.reporter.generate_category_report("all")

        self.assertEqual(report['period'], 'all')
        self.assertEqual(report['total_expenses'], 0)
        self.assertEqual(len(report['categories']), 0)

    def test_report_with_data(self):
        """Тест генерации отчета с данными."""
        self.storage.add_expense(1, 100.0, "Продукты")
        self.storage.add_expense(1, 200.0, "Ресторан")
        self.storage.add_expense(2, 150.0, "Метро")

        report = self.reporter.generate_category_report("all")

        self.assertEqual(report['total_expenses'], 450.0)
        self.assertEqual(len(report['categories']), 2)

        # Используем правильные ключи из get_category_stats
        food_cat = next(c for c in report['categories'] if c['category_name'] == 'Еда')
        self.assertEqual(food_cat['total_amount'], 300.0)  # Исправлено на total_amount
        self.assertEqual(food_cat['transaction_count'], 2)


    def test_print_report(self):
        """Тест вывода отчета в консоль."""
        self.storage.add_expense(1, 100.0, "Тест")
        report = self.reporter.generate_category_report("all")

        # Проверяем, что функция не падает с ошибкой
        try:
            self.reporter.print_report(report)
        except Exception as e:
            self.fail(f"print_report() вызвал исключение: {e}")


class TestCommandHandler(unittest.TestCase):
    """Тесты для класса CommandHandler."""

    def setUp(self):
        """Создаем тестовый обработчик команд."""
        self.test_db = "test_commands.db"
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)
        self.handler = CommandHandler()
        # Подменяем базу данных на тестовую
        self.handler.storage = Storage(self.test_db)
        self.handler.report_generator = ReportGenerator(self.handler.storage)

    def tearDown(self):
        """Удаляем тестовую базу данных."""
        if os.path.exists(self.test_db):
            os.unlink(self.test_db)


    def test_handle_add_valid(self):
        """Тест обработки команды add с валидными данными."""
        class MockArgs:
            category = "Еда"
            amount = 100.0
            description = "Тестовый расход"

        args = MockArgs()

        # Проверяем, что функция не падает с ошибкой
        try:
            self.handler.handle_add(args)
        except Exception as e:
            self.fail(f"handle_add() вызвал исключение: {e}")

    def test_handle_add_invalid_category(self):
        """Тест обработки команды add с невалидной категорией."""
        class MockArgs:
            category = "НесуществующаяКатегория"
            amount = 100.0
            description = "Тестовый расход"

        args = MockArgs()

        # Проверяем, что функция не падает с ошибкой
        try:
            self.handler.handle_add(args)
        except Exception as e:
            self.fail(f"handle_add() вызвал исключение: {e}")

    def test_handle_list(self):
        """Тест обработки команды list."""
        class MockArgs:
            period = "all"

        args = MockArgs()

        # Сначала добавляем тестовые данные
        self.handler.storage.add_expense(1, 100.0, "Тест")

        # Проверяем, что функция не падает с ошибкой
        try:
            self.handler.handle_list(args)
        except Exception as e:
            self.fail(f"handle_list() вызвал исключение: {e}")

    def test_handle_report(self):
        """Тест обработки команды report."""
        class MockArgs:
            period = "all"
            output = None

        args = MockArgs()

        # Сначала добавляем тестовые данные
        self.handler.storage.add_expense(1, 100.0, "Тест")

        # Проверяем, что функция не падает с ошибкой
        try:
            self.handler.handle_report(args)
        except Exception as e:
            self.fail(f"handle_report() вызвал исключение: {e}")

    def test_handle_delete(self):
        """Тест обработки команды delete."""
        class MockArgs:
            id = 1

        args = MockArgs()

        # Сначала добавляем тестовые данные
        self.handler.storage.add_expense(1, 100.0, "Для удаления")

        # Проверяем, что функция не падает с ошибкой
        try:
            self.handler.handle_delete(args)
        except Exception as e:
            self.fail(f"handle_delete() вызвал исключение: {e}")




if __name__ == '__main__':
    print("=== ЗАПУСК ПОЛНЫХ ТЕСТОВ ФИНАНСОВОГО ТРЕКЕРА ===")
    unittest.main(verbosity=2)