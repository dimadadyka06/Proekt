"""
Модуль обработчиков команд для CLI.

Содержит класс для обработки аргументов командной строки
и выполнения соответствующих действий.
"""

import argparse
from .storage import Storage
from .report import ReportGenerator


class CommandHandler:
    """Класс для обработки команд командной строки.

    Attributes:
        storage (Storage): Объект хранилища данных.
        report_generator (ReportGenerator): Объект генератора отчетов.
    """

    def __init__(self):
        """Инициализирует обработчик команд."""
        self.storage = Storage()
        self.report_generator = ReportGenerator(self.storage)

    def handle_add(self, args):
        """Обрабатывает команду добавления нового расхода.

        Args:
            args: Аргументы командной строки для команды add.
        """
        try:
            category_id = None
            categories = self.storage.get_categories()

            for category in categories:
                if category.name.lower() == args.category.lower():
                    category_id = category.id
                    break

            if category_id is None:
                print(f"Категория '{args.category}' не найдена!")
                print("Доступные категории:")
                for cat in categories:
                    print(f"  - {cat.name}")
                return

            success = self.storage.add_expense(
                category_id=category_id,
                amount=args.amount,
                description=args.description
            )

            if success:
                print(f"✅ Расход добавлен: {args.description} - {args.amount} ₽")
            else:
                print("❌ Ошибка при добавлении записи")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_list(self, args):
        """Обрабатывает команду просмотра расходов.

        Args:
            args: Аргументы командной строки для команды list.
        """
        try:
            expenses = self.storage.get_expenses(args.period)
            categories = {cat.id: cat for cat in self.storage.get_categories()}

            if not expenses:
                print(f"Расходы за указанный период ({args.period}) не найдены")
                return

            print(f"\n=== РАСХОДЫ ({args.period.upper()}) ===")
            total = 0

            for expense in expenses:
                category = categories.get(expense.category_id, None)
                category_name = category.name if category else "Неизвестно"

                print(f"{expense.date} | {category_name:15} | {expense.amount:8.2f} ₽ | {expense.description}")
                total += expense.amount

            print(f"\nИтого расходы: {total:.2f} ₽")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_report(self, args):
        """Обрабатывает команду генерации отчета.

        Args:
            args: Аргументы командной строки для команды report.
        """
        try:
            report = self.report_generator.generate_category_report(
                period=args.period,
                output_file=args.output
            )

            if report:
                self.report_generator.print_report(report)
            else:
                print("❌ Не удалось сгенерировать отчет")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_categories(self, args):
        """Обрабатывает команду просмотра категорий.

        Args:
            args: Аргументы командной строки для команды categories.
        """
        try:
            categories = self.storage.get_categories()

            print("\n=== КАТЕГОРИИ РАСХОДОВ ===")
            for cat in categories:
                print(f"  - {cat.name}")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def handle_delete(self, args):
        """Обрабатывает команду удаления расхода.

        Args:
            args: Аргументы командной строки для команды delete.
        """
        try:
            if self.storage.delete_expense(args.id):
                print(f"✅ Расход с ID {args.id} удален")
            else:
                print(f"❌ Расход с ID {args.id} не найден")

        except Exception as e:
            print(f"❌ Ошибка: {e}")