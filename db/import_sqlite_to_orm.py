"""Перенос данных из базы ПР7 в базу Django (через ORM).

Запуск из корня проекта после применения миграций:
    python db/import_sqlite_to_orm.py
"""
import os
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import django
from django.db import transaction

# Корень проекта: скрипт лежит в каталоге db.
BASE_DIR = Path(__file__).resolve().parent.parent

# Чтобы найти пакет настроек при запуске скрипта из каталога db.
sys.path.insert(0, str(BASE_DIR))

# Исходная база данных ПР7 (источник данных).
SOURCE_DB = BASE_DIR / "data" / "budget_planning.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budgetplan.settings")
django.setup()

# Модели импортируются только после django.setup().
from budgets.models import Budget, BudgetItem  # noqa: E402
from departments.models import Department  # noqa: E402


def read_source():
    """Прочитать все таблицы исходной базы."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    connection = sqlite3.connect(SOURCE_DB)
    connection.row_factory = sqlite3.Row
    try:
        departments = connection.execute(
            "SELECT id, name, head FROM departments ORDER BY id"
        ).fetchall()
        budgets = connection.execute(
            """
            SELECT id, department_id, period, period_start, period_end
            FROM budgets
            ORDER BY id
            """
        ).fetchall()
        items = connection.execute(
            """
            SELECT id, budget_id, category, planned
            FROM budget_items
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()

    return departments, budgets, items


def main():
    departments, budgets, items = read_source()

    # Одна транзакция: при ошибке изменения откатываются.
    with transaction.atomic():
        # Порядок важен: сначала независимые сущности.
        for row in departments:
            Department.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "head": row["head"],
                },
            )

        for row in budgets:
            Budget.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "department_id": row["department_id"],
                    "period": row["period"],
                    # Строки YYYY-MM-DD превращаются в объекты date.
                    "period_start": date.fromisoformat(
                        row["period_start"]
                    ),
                    "period_end": date.fromisoformat(row["period_end"]),
                },
            )

        for row in items:
            BudgetItem.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "budget_id": row["budget_id"],
                    # Сумму храним как Decimal, а не как float.
                    "planned": Decimal(str(row["planned"])),
                    "category": row["category"],
                },
            )

    print("Перенос данных завершён.")
    print(f"Подразделений: {Department.objects.count()}")
    print(f"Бюджетов: {Budget.objects.count()}")
    print(f"Статей: {BudgetItem.objects.count()}")


if __name__ == "__main__":
    main()
