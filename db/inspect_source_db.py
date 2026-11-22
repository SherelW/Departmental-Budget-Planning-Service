"""Исследование структуры исходной базы ПР7 (только чтение)."""
import sqlite3
from pathlib import Path

# Файл находится в каталоге db, корень проекта – на уровень выше.
BASE_DIR = Path(__file__).resolve().parent.parent

# Исходная база, созданная в ПР7.
SOURCE_DB = BASE_DIR / "data" / "budget_planning.sqlite"

if not SOURCE_DB.exists():
    raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

with sqlite3.connect(SOURCE_DB) as connection:
    connection.row_factory = sqlite3.Row

    # Пользовательские таблицы базы данных.
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    for (table_name,) in tables:
        print(f"\nТаблица: {table_name}")

        # Имена, типы, признаки NOT NULL и первичный ключ.
        columns = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        print("Столбцы:")
        for column in columns:
            print(
                f" имя={column['name']}, "
                f"тип={column['type']}, "
                f"NOT NULL={column['notnull']}, "
                f"PRIMARY KEY={column['pk']}"
            )

        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        print(f"Количество записей: {count}")

    # Проверка связей: ссылки должны указывать на существующие записи.
    orphan_budgets = connection.execute(
        """
        SELECT COUNT(*)
        FROM budgets AS b
        LEFT JOIN departments AS d ON d.id = b.department_id
        WHERE d.id IS NULL
        """
    ).fetchone()[0]
    orphan_items = connection.execute(
        """
        SELECT COUNT(*)
        FROM budget_items AS bi
        LEFT JOIN budgets AS b ON b.id = bi.budget_id
        WHERE b.id IS NULL
        """
    ).fetchone()[0]

    print("\nПроверка связей:")
    print(f" бюджетов без подразделения: {orphan_budgets}")
    print(f" статей без бюджета: {orphan_items}")
