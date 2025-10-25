
"""
Финансовый трекер расходов
"""

import argparse
import sys
from fintracker.command import CommandHandler


def main():
    parser = argparse.ArgumentParser(description='Финансовый трекер расходов')
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    add_parser = subparsers.add_parser('add', help='Добавить новый расход')
    add_parser.add_argument('--category', '-c', required=True, help='Категория расхода')
    add_parser.add_argument('--amount', '-a', type=float, required=True, help='Сумма')
    add_parser.add_argument('--description', '-d', required=True, help='Описание')

    list_parser = subparsers.add_parser('list', help='Просмотреть расходы')
    list_parser.add_argument('--period', '-p', choices=['day', 'week', 'month', 'year', 'all'],
                             default='month', help='Период для отображения')

    report_parser = subparsers.add_parser('report', help='Сгенерировать отчет')
    report_parser.add_argument('--period', '-p', choices=['day', 'week', 'month', 'year', 'all'],
                               default='month', help='Период для отчета')
    report_parser.add_argument('--output', '-o', help='Файл для сохранения отчета (JSON или CSV)')

    subparsers.add_parser('categories', help='Показать доступные категории')

    delete_parser = subparsers.add_parser('delete', help='Удалить расход по ID')
    delete_parser.add_argument('--id', '-i', type=int, required=True, help='ID расхода для удаления')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    handler = CommandHandler()

    try:
        if args.command == 'add':
            handler.handle_add(args)
        elif args.command == 'list':
            handler.handle_list(args)
        elif args.command == 'report':
            handler.handle_report(args)
        elif args.command == 'categories':
            handler.handle_categories(args)
        elif args.command == 'delete':
            handler.handle_delete(args)
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()