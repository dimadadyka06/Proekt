import json
import os
from typing import List
from datetime import date
from .models import Expense, Category


class Storage:
    def __init__(self, data_file: str = "expenses_data.json"):
        self.data_file = data_file
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
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

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка загрузки данных: {e}")
            return {'expenses': [], 'categories': [], 'next_id': 1}

    def _save_data(self, data: dict):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Ошибка сохранения данных: {e}")

    def add_expense(self, category_id: int, amount: float, description: str, expense_date: str = None) -> bool:
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
        try:
            data = self._load_data()
            return [Category.from_dict(cat) for cat in data['categories']]
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            return []

    def delete_expense(self, expense_id: int) -> bool:
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