import sqlite3

from django.shortcuts import render

from db.database import get_connection


def departments(request):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        departments_data = conn.execute("""
            SELECT
                id,
                name,
                head
            FROM departments
            ORDER BY name;
        """).fetchall()
    finally:
        conn.close()

    context = {
        "departments": departments_data,
    }

    return render(
        request,
        "departments/department_list.html",
        context,
    )


def department_detail(request, department_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        department = conn.execute("""
            SELECT
                id,
                name,
                head
            FROM departments
            WHERE id = ?;
        """, [department_id]).fetchone()

        budgets_data = []
        items = []
        total = 0
        if department is not None:
            budgets_data = conn.execute("""
                SELECT
                    b.id,
                    b.period,
                    COALESCE(SUM(bi.planned), 0) AS total
                FROM budgets AS b
                LEFT JOIN budget_items AS bi
                    ON bi.budget_id = b.id
                WHERE b.department_id = ?
                GROUP BY b.id, b.period
                ORDER BY b.period_start;
            """, [department_id]).fetchall()

            items = conn.execute("""
                SELECT
                    b.id AS budget_id,
                    b.period,
                    bi.category,
                    bi.planned
                FROM budget_items AS bi
                JOIN budgets AS b
                    ON bi.budget_id = b.id
                WHERE b.department_id = ?
                ORDER BY b.period_start, bi.planned DESC;
            """, [department_id]).fetchall()

            total = conn.execute("""
                SELECT
                    COALESCE(SUM(bi.planned), 0) AS total
                FROM budget_items AS bi
                JOIN budgets AS b
                    ON bi.budget_id = b.id
                WHERE b.department_id = ?;
            """, [department_id]).fetchone()["total"]
    finally:
        conn.close()

    context = {
        "department": department,
        "budgets": budgets_data,
        "items": items,
        "total": total,
    }

    return render(
        request,
        "departments/department_detail.html",
        context,
        status=404 if department is None else 200,
    )
