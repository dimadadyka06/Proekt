"""
Модуль для работы с хранением данных.

Обеспечивает сохранение, загрузку и управление данными о расходах
в JSON-файле.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import date
from .models import Expense, Category


class Storage:
    """Класс для управления хранением данных о расходах.

    Attributes:
        data_file (str): Путь к файлу с данными.
    """

    def __init__(self, data_file: str = "expenses_data.json"):
        """Инициализирует хранилище данных.

        Args:
            data_file (str, optional): Путь к файлу с данными.
                По умолчанию "expenses_data.json".
        """
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Создает файл данных с начальной структурой, если он не существует."""
        if not os.path.exists(self.data_file):
            initial_data = {
                'expenses': [],
                'categories': [
                    {'id': 1, 'name': 'Еда'},
                    {'id': 2, 'name': 'Транспорт'},
                    {'id': 3, 'name': 'Развлечения'},
                    {'id': 4, 'name': 'Коммунальные'},
                    {'id': 5, 'name': 'Одежда'},
                    {'id': 6, 'name': 'Здоровье'}
                ],
                'next_id': 1
            }
            self._save_data(initial_data)

    def _load_data(self) -> Dict:
        """Загружает данные из JSON-файла.

        Returns:
            Dict: Словарь с данными из файла.

        Raises:
            FileNotFoundError: Если файл не найден.
            json.JSONDecodeError: Если файл содержит некорректный JSON.
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки данных: {e}")
            return {'expenses': [], 'categories': [], 'next_id': 1}

    def _save_data(self, data: Dict):
        """Сохраняет данные в JSON-файл.

        Args:
            data (Dict): Данные для сохранения.

        Raises:
            IOError: Если произошла ошибка записи в файл.
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка сохранения данных: {e}")

    def add_expense(self, category_id: int, amount: float, description: str,
                    expense_date: Optional[str] = None) -> bool:
        """Добавляет новую запись о расходе.

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
            data = self._load_data()

            if expense_date is None:
                expense_date = date.today().isoformat()

            expense = Expense(
                id=data['next_id'],
                category_id=category_id,
                amount=amount,
                description=description,
                date=expense_date
            )

            data['expenses'].append(expense.to_dict())
            data['next_id'] += 1

            self._save_data(data)
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
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
            data = self._load_data()
            expenses = [Expense.from_dict(exp) for exp in data['expenses']]

            if period == "all":
                return expenses

            today = date.today()
            filtered_expenses = []

            for expense in expenses:
                expense_date = date.fromisoformat(expense.date)

                if period == "day" and expense_date == today:
                    filtered_expenses.append(expense)
                elif period == "week":
                    days_diff = (today - expense_date).days
                    if 0 <= days_diff <= 7:
                        filtered_expenses.append(expense)
                elif period == "month" and expense_date.month == today.month and expense_date.year == today.year:
                    filtered_expenses.append(expense)
                elif period == "year" and expense_date.year == today.year:
                    filtered_expenses.append(expense)

            return filtered_expenses
        except Exception as e:
            print(f"Ошибка при получении записей: {e}")
            return []

    def get_categories(self) -> List[Category]:
        """Возвращает список всех категорий.

        Returns:
            List[Category]: Список объектов Category.
        """
        try:
            data = self._load_data()
            return [Category.from_dict(cat) for cat in data['categories']]
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []

    def delete_expense(self, expense_id: int) -> bool:
        """Удаляет запись о расходе по ID.

        Args:
            expense_id (int): ID записи для удаления.

        Returns:
            bool: True если запись удалена, False если запись не найдена.
        """
        try:
            data = self._load_data()
            initial_count = len(data['expenses'])
            data['expenses'] = [exp for exp in data['expenses'] if exp['id'] != expense_id]

            if len(data['expenses']) < initial_count:
                self._save_data(data)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при удалении записи: {e}")
            return False