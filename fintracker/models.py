"""
Модуль моделей данных для финансового трекера.

Содержит классы для представления категорий и записей о расходах.
"""

import json
from datetime import date
from typing import Dict


class Category:
    """Класс для представления категории расходов.

    Attributes:
        id (int): Уникальный идентификатор категории.
        name (str): Название категории.
    """

    def __init__(self, id: int, name: str):
        """Инициализирует объект категории.

        Args:
            id (int): Уникальный идентификатор категории.
            name (str): Название категории.
        """
        self.id = id
        self.name = name

    def to_dict(self) -> Dict:
        """Преобразует объект категории в словарь.

        Returns:
            Dict: Словарь с данными категории.
        """
        return {
            'id': self.id,
            'name': self.name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Category':
        """Создает объект категории из словаря.

        Args:
            data (Dict): Словарь с данными категории.

        Returns:
            Category: Новый объект категории.
        """
        return cls(
            id=data['id'],
            name=data['name']
        )


class Expense:
    """Класс для представления записи о расходе.

    Attributes:
        id (int): Уникальный идентификатор записи.
        category_id (int): ID категории расхода.
        amount (float): Сумма расхода.
        description (str): Описание расхода.
        date (str): Дата расхода в формате YYYY-MM-DD.
    """

    def __init__(self, id: int, category_id: int, amount: float, description: str, date: str):
        """Инициализирует объект записи о расходе.

        Args:
            id (int): Уникальный идентификатор записи.
            category_id (int): ID категории расхода.
            amount (float): Сумма расхода.
            description (str): Описание расхода.
            date (str): Дата расхода в формате YYYY-MM-DD.
        """
        self.id = id
        self.category_id = category_id
        self.amount = amount
        self.description = description
        self.date = date

    def to_dict(self) -> Dict:
        """Преобразует объект расхода в словарь.

        Returns:
            Dict: Словарь с данными расхода.
        """
        return {
            'id': self.id,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        """Создает объект расхода из словаря.

        Args:
            data (Dict): Словарь с данными расхода.

        Returns:
            Expense: Новый объект расхода.
        """
        return cls(
            id=data['id'],
            category_id=data['category_id'],
            amount=data['amount'],
            description=data['description'],
            date=data['date']
        )