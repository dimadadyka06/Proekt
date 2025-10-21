import csv
import json
from typing import List, Dict
from datetime import datetime
from .models import Expense, Category


class ReportGenerator:
    def __init__(self, storage):
        self.storage = storage

    def generate_category_report(self, period: str = "month", output_file: str = None) -> Dict:
        try:
            expenses = self.storage.get_expenses(period)
            categories = self.storage.get_categories()

            category_totals = {}
            category_counts = {}

            for category in categories:
                category_totals[category.id] = {'amount': 0, 'name': category.name}
                category_counts[category.id] = 0

            for expense in expenses:
                cat_id = expense.category_id
                if cat_id in category_totals:
                    category_totals[cat_id]['amount'] += expense.amount
                    category_counts[cat_id] += 1

            report = {
                'period': period,
                'generated_at': datetime.now().isoformat(),
                'total_expenses': sum(cat['amount'] for cat in category_totals.values()),
                'categories': []
            }

            for cat_id, totals in category_totals.items():
                if totals['amount'] > 0:
                    report['categories'].append({
                        'category_name': totals['name'],
                        'amount': totals['amount'],
                        'transaction_count': category_counts[cat_id]
                    })

            if output_file:
                self._save_report_to_file(report, output_file)

            return report
        except Exception as e:
            print(f"Ошибка при генерации отчета: {e}")
            return {}

    def _save_report_to_file(self, report: Dict, output_file: str):
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
                            category['amount'],
                            category['transaction_count']
                        ])

                    writer.writerow([])
                    writer.writerow(['Итого расходы:', report['total_expenses']])

            print(f"Отчет сохранен в файл: {output_file}")

        except Exception as e:
            print(f"Ошибка при сохранении отчета: {e}")

    def print_report(self, report: Dict):
        print(f"\n=== ОТЧЕТ ПО РАСХОДАМ ===")
        print(f"Период: {report['period']}")
        print(f"Сгенерирован: {report['generated_at']}")
        print(f"\n--- По категориям ---")

        for category in report['categories']:
            print(f"{category['category_name']}:")
            print(f"  Сумма: {category['amount']:.2f} ₽")
            print(f"  Операций: {category['transaction_count']}")
            print()

        print(f"Итого расходы: {report['total_expenses']:.2f} ₽")