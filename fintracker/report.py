"""
Модуль для генерации отчетов по расходам из базы данных.
"""

import csv
import json
from typing import List, Dict, Optional
from datetime import datetime
from .models import Expense, Category
from .database import Database


class ReportGenerator:
    """Класс для генерации финансовых отчетов из БД.

    Attributes:
        database (Database): Объект базы данных для доступа к данным.
    """

    def __init__(self, storage):
        """Инициализирует генератор отчетов.

        Args:
            storage (Storage): Объект хранилища данных.
        """
        self.storage = storage
        self.database = storage.database

    def generate_category_report(self, period: str = "month", output_file: Optional[str] = None) -> Dict:
        """Генерирует отчет по расходам по категориям из БД.

        Args:
            period (str, optional): Период для отчета.
                Допустимые значения: "day", "week", "month", "year", "all".
                По умолчанию "month".
            output_file (Optional[str], optional): Путь для сохранения отчета.
                Если указан, отчет сохраняется в файл.

        Returns:
            Dict: Словарь с данными отчета.
        """
        try:
            # Используем метод базы данных для получения статистики
            category_stats = self.database.get_category_stats(period)

            total_expenses = sum(stat['total_amount'] for stat in category_stats)

            report = {
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'total_expenses': total_expenses,
                'categories': category_stats
            }

            if output_file:
                self._save_report_to_file(report, output_file)

            return report
        except Exception as e:
            print(f"Ошибка при генерации отчета: {e}")
            return {}

    def _save_report_to_file(self, report: Dict, output_file: str):
        """Сохраняет отчет в файл в указанном формате.

        Args:
            report (Dict): Данные отчета.
            output_file (str): Путь к файлу для сохранения.
        """
        try:
            if output_file.endswith('.json'):
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)

            elif output_file.endswith('.csv'):
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Категория', 'Сумма расходов', 'Количество операций'])

                    for category in report['categories']:
                        writer.writerow([
                            category['category_name'],
                            category['total_amount'],
                            category['transaction_count']
                        ])

                    writer.writerow([])
                    writer.writerow(['Итого расходы:', report['total_expenses']])

            print(f"Отчет сохранен в файл: {output_file}")

        except Exception as e:
            print(f"Ошибка при сохранении отчета: {e}")

    def print_report(self, report: Dict):
        """Выводит отчет в консоль в удобочитаемом формате.

        Args:
            report (Dict): Данные отчета для вывода.
        """
        print(f"\n=== ОТЧЕТ ПО РАСХОДАМ ===")
        print(f"Период: {report['period']}")
        print(f"Сгенерирован: {report['generated_at']}")
        print(f"\n--- По категориям ---")

        for category in report['categories']:
            print(f"{category['category_name']}:")
            print(f"  Сумма: {category['total_amount']:.2f} ₽")
            print(f"  Операций: {category['transaction_count']}")
            print()

        print(f"Итого расходы: {report['total_expenses']:.2f} ₽")