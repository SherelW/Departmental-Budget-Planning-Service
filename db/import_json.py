import re
from datetime import date
from pathlib import Path

from db.database import BASE_DIR, get_connection
from storage import load_planning

PLANNING_FILE = Path(BASE_DIR) / "data" / "planning.json"
DATE_PATTERN = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")


def parse_period(period):
    """'01.09.2026 - 30.09.2026' -> ('2026-09-01', '2026-09-30')."""
    found = DATE_PATTERN.findall(period)
    if not found or len(found) > 2:
        raise ValueError(f"Не удалось разобрать период: {period!r}")
    dates = [date(int(y), int(m), int(d)).isoformat() for d, m, y in found]
    return dates[0], dates[-1]


def import_departments(conn, planning):
    conn.executemany(
        """
        INSERT INTO departments (id, name, head)
        VALUES (?, ?, ?)
        """,
        [
            (department.id, department.name, department.head)
            for department in planning.get_departments()
        ],
    )


def import_budgets(conn, planning):
    rows = []
    for budget in planning.budgets:
        start, end = parse_period(budget.period)
        rows.append(
            (budget.id, budget.department.id, budget.period, start, end)
        )
    conn.executemany(
        """
        INSERT INTO budgets (
            id, department_id, period, period_start, period_end
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )


def import_items(conn, planning):
    conn.executemany(
        """
        INSERT INTO budget_items (budget_id, category, planned)
        VALUES (?, ?, ?)
        """,
        [
            (budget.id, item.category, item.planned)
            for budget in planning.budgets
            for item in budget.items
        ],
    )


def main():
    planning = load_planning(PLANNING_FILE)
    conn = get_connection()
    try:
        # порядок важен: сначала таблицы, на которые ссылаются внешние ключи
        import_departments(conn, planning)
        import_budgets(conn, planning)
        import_items(conn, planning)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
