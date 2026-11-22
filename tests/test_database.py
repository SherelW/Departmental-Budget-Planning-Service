import sqlite3
from pathlib import Path

import pytest

from db import database, import_json
from storage import load_planning

QUERIES_FILE = Path(__file__).resolve().parent.parent / "sql" / "queries.sql"


def make_db(tmp_path, monkeypatch):
    """Создать временную БД: схема + импорт из data/planning.json."""
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.sqlite")
    conn = database.get_connection()
    database.init_schema(conn)
    conn.close()
    import_json.main()
    conn = database.get_connection()
    conn.row_factory = sqlite3.Row
    return conn


def read_queries():
    """Разобрать sql/queries.sql на отдельные запросы."""
    queries, buffer = [], ""
    for line in QUERIES_FILE.read_text(encoding="utf-8").splitlines(True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            body = "\n".join(
                row for row in buffer.splitlines()
                if not row.strip().startswith("--")
            ).strip()
            if body:
                queries.append(body)
            buffer = ""
    return queries


def test_tables_created(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    names = {
        row["name"] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"departments", "budgets", "budget_items"} <= names
    conn.close()


def test_schema_can_be_applied_twice(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    database.init_schema(conn)
    conn.close()


def test_import_matches_json(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    planning = load_planning(import_json.PLANNING_FILE)
    count = lambda table: conn.execute(  # noqa: E731
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]
    assert count("departments") == len(planning.get_departments())
    assert count("budgets") == len(planning.budgets)
    assert count("budget_items") == sum(len(b.items) for b in planning.budgets)
    conn.close()


def test_period_is_split_into_iso_dates(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    row = conn.execute(
        "SELECT period_start, period_end FROM budgets WHERE id = 1"
    ).fetchone()
    assert (row["period_start"], row["period_end"]) == (
        "2026-09-01", "2026-09-30",
    )
    conn.close()


def test_foreign_keys_are_enforced(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO budgets "
            "(department_id, period, period_start, period_end) "
            "VALUES (999, 'p', '2026-01-01', '2026-01-31')"
        )
    conn.close()


def test_planned_must_be_positive(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO budget_items (budget_id, category, planned) "
            "VALUES (1, 'Плохая статья', -5)"
        )
    conn.close()


def test_parse_period():
    assert import_json.parse_period("01.09.2026 - 30.09.2026") == (
        "2026-09-01", "2026-09-30",
    )
    assert import_json.parse_period("15.09.2026") == (
        "2026-09-15", "2026-09-15",
    )
    with pytest.raises(ValueError):
        import_json.parse_period("сентябрь")


def test_all_queries_from_file_run(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    queries = read_queries()
    assert len(queries) >= 10
    for query in queries:
        conn.execute(query).fetchall()
    conn.close()


def test_free_departments_on_date(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    query = """
        SELECT name FROM departments
        WHERE id NOT IN (
            SELECT department_id FROM budgets
            WHERE ? BETWEEN period_start AND period_end
        )
    """
    assert conn.execute(query, ["2026-09-15"]).fetchall() == []
    assert len(conn.execute(query, ["2026-10-15"]).fetchall()) == 2
    assert len(conn.execute(query, ["2027-01-01"]).fetchall()) == 3
    conn.close()


def test_parameter_is_not_executed_as_sql(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    rows = conn.execute(
        "SELECT id FROM departments WHERE name = ?",
        ["x' OR '1'='1"],
    ).fetchall()
    assert rows == []
    conn.close()


def test_having_filters_groups(tmp_path, monkeypatch):
    conn = make_db(tmp_path, monkeypatch)
    query = """
        SELECT budget_id, SUM(planned) AS total FROM budget_items
        GROUP BY budget_id HAVING SUM(planned) >= ?
    """
    assert len(conn.execute(query, [600_000]).fetchall()) == 1
    assert len(conn.execute(query, [500_000]).fetchall()) == 4
    assert conn.execute(query, [5_000_000]).fetchall() == []
    conn.close()
