import math
import sqlite3
from datetime import date

from django.shortcuts import render

from db.database import get_connection

DEFAULT_MIN_TOTAL = 600_000
LARGE_ITEM = 200_000


def budgets(request):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        budgets_data = conn.execute("""
            SELECT
                b.id,
                b.period,
                d.name AS department_name,
                COALESCE(SUM(bi.planned), 0) AS total
            FROM budgets AS b
            JOIN departments AS d
                ON b.department_id = d.id
            LEFT JOIN budget_items AS bi
                ON bi.budget_id = b.id
            GROUP BY b.id, b.period, d.name
            ORDER BY b.period_start, d.name;
        """).fetchall()

        period_totals = conn.execute("""
            SELECT
                b.period,
                SUM(bi.planned) AS total
            FROM budgets AS b
            JOIN budget_items AS bi
                ON bi.budget_id = b.id
            GROUP BY b.period
            ORDER BY MIN(b.period_start);
        """).fetchall()
    finally:
        conn.close()

    context = {
        "budgets": budgets_data,
        "period_totals": period_totals,
    }

    return render(
        request,
        "budgets/budget_list.html",
        context,
    )


def budget_detail(request, budget_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        budget = conn.execute("""
            SELECT
                b.id,
                b.period,
                d.id AS department_id,
                d.name AS department_name,
                d.head AS department_head,
                (
                    SELECT COALESCE(SUM(bi.planned), 0)
                    FROM budget_items AS bi
                    WHERE bi.budget_id = b.id
                ) AS total
            FROM budgets AS b
            JOIN departments AS d
                ON b.department_id = d.id
            WHERE b.id = ?;
        """, [budget_id]).fetchone()

        items = []
        if budget is not None:
            items = conn.execute("""
                SELECT
                    category,
                    planned
                FROM budget_items
                WHERE budget_id = ?
                ORDER BY planned DESC;
            """, [budget_id]).fetchall()
    finally:
        conn.close()

    context = {
        "budget": budget,
        "items": items,
    }

    return render(
        request,
        "budgets/budget_detail.html",
        context,
        status=404 if budget is None else 200,
    )


def budget_search(request):
    date_text = request.GET.get("date", "")
    error = None
    searched = False
    budgets_on_date = []
    free_departments = []

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        periods = conn.execute("""
            SELECT DISTINCT
                period,
                period_start
            FROM budgets
            ORDER BY period_start;
        """).fetchall()

        if date_text:
            try:
                date.fromisoformat(date_text)
            except ValueError:
                error = "Некорректная дата. Выберите дату в календаре."
            else:
                searched = True
                budgets_on_date = conn.execute("""
                    SELECT
                        b.id,
                        b.period,
                        d.name AS department_name,
                        d.head AS department_head
                    FROM budgets AS b
                    JOIN departments AS d
                        ON b.department_id = d.id
                    WHERE ? BETWEEN b.period_start AND b.period_end
                    ORDER BY d.name;
                """, [date_text]).fetchall()

                free_departments = conn.execute("""
                    SELECT
                        id,
                        name,
                        head
                    FROM departments
                    WHERE id NOT IN (
                        SELECT department_id
                        FROM budgets
                        WHERE ? BETWEEN period_start AND period_end
                    )
                    ORDER BY name;
                """, [date_text]).fetchall()
    finally:
        conn.close()

    context = {
        "date": date_text,
        "error": error,
        "searched": searched,
        "budgets": budgets_on_date,
        "free_departments": free_departments,
        "periods": periods,
    }

    return render(
        request,
        "budgets/budget_search.html",
        context,
    )


def statistics(request):
    min_total = DEFAULT_MIN_TOTAL
    error = None
    min_total_text = request.GET.get("min_total", "")
    if min_total_text:
        try:
            min_total = float(min_total_text)
            if not math.isfinite(min_total) or min_total < 0:
                raise ValueError
        except ValueError:
            min_total = DEFAULT_MIN_TOTAL
            error = "Минимальная сумма должна быть неотрицательным числом."

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        budgets_count = conn.execute("""
            SELECT
                COUNT(*) AS budgets_count
            FROM budgets;
        """).fetchone()["budgets_count"]

        totals = conn.execute("""
            SELECT
                COALESCE(SUM(planned), 0) AS total_planned,
                COALESCE(AVG(planned), 0) AS avg_item,
                COALESCE(MIN(planned), 0) AS min_item,
                COALESCE(MAX(planned), 0) AS max_item
            FROM budget_items;
        """).fetchone()

        by_department = conn.execute("""
            SELECT
                d.name AS department_name,
                COUNT(DISTINCT b.id) AS budgets_count,
                COALESCE(SUM(bi.planned), 0) AS total
            FROM departments AS d
            LEFT JOIN budgets AS b
                ON b.department_id = d.id
            LEFT JOIN budget_items AS bi
                ON bi.budget_id = b.id
            GROUP BY d.id, d.name
            ORDER BY total DESC;
        """).fetchall()

        by_category = conn.execute("""
            SELECT
                category,
                COUNT(*) AS items_count,
                SUM(planned) AS total
            FROM budget_items
            GROUP BY category
            ORDER BY total DESC;
        """).fetchall()

        top_items = conn.execute("""
            SELECT
                category,
                planned
            FROM budget_items
            ORDER BY planned DESC, category
            LIMIT 3 OFFSET 0;
        """).fetchall()

        large_items = conn.execute("""
            SELECT
                category,
                planned
            FROM budget_items
            WHERE planned >= ?
            ORDER BY planned DESC;
        """, [LARGE_ITEM]).fetchall()

        large_budgets = conn.execute("""
            SELECT
                b.id,
                b.period,
                d.name AS department_name,
                SUM(bi.planned) AS total
            FROM budgets AS b
            JOIN departments AS d
                ON b.department_id = d.id
            JOIN budget_items AS bi
                ON bi.budget_id = b.id
            GROUP BY b.id, b.period, d.name
            HAVING SUM(bi.planned) >= ?
            ORDER BY total DESC;
        """, [min_total]).fetchall()

        busy_departments = conn.execute("""
            SELECT
                d.name AS department_name,
                COUNT(b.id) AS budgets_count
            FROM departments AS d
            JOIN budgets AS b
                ON b.department_id = d.id
            GROUP BY d.id, d.name
            HAVING COUNT(b.id) > 1
            ORDER BY budgets_count DESC;
        """).fetchall()
    finally:
        conn.close()

    context = {
        "budgets_count": budgets_count,
        "totals": totals,
        "by_department": by_department,
        "by_category": by_category,
        "top_items": top_items,
        "large_items": large_items,
        "large_item_limit": LARGE_ITEM,
        "large_budgets": large_budgets,
        "min_total": min_total,
        "error": error,
        "busy_departments": busy_departments,
    }

    return render(
        request,
        "budgets/statistics.html",
        context,
    )
