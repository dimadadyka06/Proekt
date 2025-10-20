from typing import Dict


class Category:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Category':
        return cls(
            id=data['id'],
            name=data['name']
        )


class Expense:
    def __init__(self, id: int, category_id: int, amount: float, description: str, date: str):
        self.id = id
        self.category_id = category_id
        self.amount = amount
        self.description = description
        self.date = date

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'category_id': self.category_id,
            'amount': self.amount,
            'description': self.description,
            'date': self.date
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        return cls(
            id=data['id'],
            category_id=data['category_id'],
            amount=data['amount'],
            description=data['description'],
            date=data['date']
        )