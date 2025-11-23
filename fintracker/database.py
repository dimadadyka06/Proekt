"""
Модуль для работы с базой данных SQLite.

Обеспечивает создание базы данных, таблиц и основные операции с данными.
"""

import sqlite3
import os
from typing import List, Optional
from datetime import date
from .models import Category, Expense


class Database:
    """Класс для управления базой данных финансового трекера.

    Attributes:
        db_path (str): Путь к файлу базы данных.
    """

    def __init__(self, db_path: str = "finance_tracker.db"):
        """Инициализирует подключение к базе данных.

        Args:
            db_path (str, optional): Путь к файлу базы данных.
                По умолчанию "finance_tracker.db".
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Инициализирует базу данных и создает таблицы если они не существуют."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Создаем таблицу категорий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            # Создаем таблицу расходов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            # Добавляем начальные категории если таблица пустая
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                initial_categories = [
                    (1, 'Еда'),
                    (2, 'Транспорт'),
                    (3, 'Развлечения'),
                    (4, 'Коммунальные'),
                    (5, 'Одежда'),
                    (6, 'Здоровье')
                ]
                cursor.executemany(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    initial_categories
                )

            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Создает и возвращает соединение с базой данных.

        Returns:
            sqlite3.Connection: Объект соединения с базой данных.
        """
        return sqlite3.connect(self.db_path)

    def add_expense(self, category_id: int, amount: float, description: str,
                    expense_date: Optional[str] = None) -> bool:
        """Добавляет новую запись о расходе в базу данных.

        Args:
            category_id (int): ID категории расхода.
            amount (float): Сумма расхода.
            description (str): Описание расхода.
            expense_date (Optional[str], optional): Дата расхода.
                Если не указана, используется текущая дата.

        Returns:
            bool: True если запись успешно добавлена, False в случае ошибки.
        """
        try:
            if expense_date is None:
                expense_date = date.today().isoformat()

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO expenses (category_id, amount, description, date)
                    VALUES (?, ?, ?, ?)
                ''', (category_id, amount, description, expense_date))
                conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка при добавлении записи в БД: {e}")
            return False

    def get_expenses(self, period: str = "all") -> List[Expense]:
        """Возвращает список расходов за указанный период.

        Args:
            period (str, optional): Период для фильтрации.
                Допустимые значения: "day", "week", "month", "year", "all".
                По умолчанию "all".

        Returns:
            List[Expense]: Список объектов Expense за указанный период.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Базовый запрос
                query = '''
                    SELECT e.id, e.category_id, e.amount, e.description, e.date
                    FROM expenses e
                '''
                params = []

                # Добавляем фильтрацию по периоду
                if period != "all":
                    today = date.today()

                    if period == "day":
                        query += " WHERE e.date = ?"
                        params.append(today.isoformat())
                    elif period == "week":
                        week_ago = (today - date.today().replace(day=today.day - 7)).isoformat()
                        query += " WHERE e.date BETWEEN ? AND ?"
                        params.extend([week_ago, today.isoformat()])
                    elif period == "month":
                        query += " WHERE strftime('%Y-%m', e.date) = strftime('%Y-%m', 'now')"
                    elif period == "year":
                        query += " WHERE strftime('%Y', e.date) = strftime('%Y', 'now')"

                query += " ORDER BY e.date DESC, e.id DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                expenses = []
                for row in rows:
                    expense = Expense(
                        id=row[0],
                        category_id=row[1],
                        amount=row[2],
                        description=row[3],
                        date=row[4]
                    )
                    expenses.append(expense)

                return expenses
        except Exception as e:
            print(f"Ошибка при получении записей из БД: {e}")
            return []

    def get_categories(self) -> List[Category]:
        """Возвращает список всех категорий из базы данных.

        Returns:
            List[Category]: Список объектов Category.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM categories ORDER BY id")
                rows = cursor.fetchall()

                categories = []
                for row in rows:
                    category = Category(id=row[0], name=row[1])
                    categories.append(category)

                return categories
        except Exception as e:
            print(f"Ошибка при получении категорий из БД: {e}")
            return []

    def delete_expense(self, expense_id: int) -> bool:
        """Удаляет запись о расходе по ID.

        Args:
            expense_id (int): ID записи для удаления.

        Returns:
            bool: True если запись удалена, False если запись не найдена.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при удалении записи из БД: {e}")
            return False

    def get_category_stats(self, period: str = "all") -> List[dict]:
        """Возвращает статистику по категориям за указанный период.

        Args:
            period (str, optional): Период для статистики.

        Returns:
            List[dict]: Список словарей со статистикой по категориям.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                query = '''
                    SELECT 
                        c.id,
                        c.name,
                        COUNT(e.id) as transaction_count,
                        COALESCE(SUM(e.amount), 0) as total_amount
                    FROM categories c
                    LEFT JOIN expenses e ON c.id = e.category_id
                '''
                params = []

                # Добавляем фильтрацию по периоду
                if period != "all":
                    if period == "month":
                        query += " AND strftime('%Y-%m', e.date) = strftime('%Y-%m', 'now')"
                    elif period == "year":
                        query += " AND strftime('%Y', e.date) = strftime('%Y', 'now')"
                    elif period == "week":
                        # Для недели нужна более сложная логика
                        pass

                query += '''
                    GROUP BY c.id, c.name
                    HAVING total_amount > 0
                    ORDER BY total_amount DESC
                '''

                cursor.execute(query, params)
                rows = cursor.fetchall()

                stats = []
                for row in rows:
                    stats.append({
                        'category_id': row[0],
                        'category_name': row[1],
                        'transaction_count': row[2],
                        'total_amount': row[3]
                    })

                return stats
        except Exception as e:
            print(f"Ошибка при получении статистики из БД: {e}")
            return []