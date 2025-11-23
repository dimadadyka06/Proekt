"""
Модуль для работы с хранением данных в SQLite базе данных.
"""

from typing import List, Optional
from datetime import date
from .models import Expense, Category
from .database import Database


class Storage:
    """Класс для управления хранением данных о расходах в БД.

    Attributes:
        database (Database): Объект для работы с базой данных.
    """

    def __init__(self, db_path: str = "finance_tracker.db"):
        """Инициализирует хранилище данных.

        Args:
            db_path (str, optional): Путь к файлу базы данных.
                По умолчанию "finance_tracker.db".
        """
        self.database = Database(db_path)

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
        return self.database.add_expense(category_id, amount, description, expense_date)

    def get_expenses(self, period: str = "all") -> List[Expense]:
        """Возвращает список расходов за указанный период.

        Args:
            period (str, optional): Период для фильтрации.
                Допустимые значения: "day", "week", "month", "year", "all".
                По умолчанию "all".

        Returns:
            List[Expense]: Список объектов Expense за указанный период.
        """
        return self.database.get_expenses(period)

    def get_categories(self) -> List[Category]:
        """Возвращает список всех категорий.

        Returns:
            List[Category]: Список объектов Category.
        """
        return self.database.get_categories()

    def delete_expense(self, expense_id: int) -> bool:
        """Удаляет запись о расходе по ID.

        Args:
            expense_id (int): ID записи для удаления.

        Returns:
            bool: True если запись удалена, False если запись не найдена.
        """
        return self.database.delete_expense(expense_id)