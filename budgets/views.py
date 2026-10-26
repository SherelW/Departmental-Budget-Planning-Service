from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import money, page
from storage import load_planning


def budgets(request):
    planning = load_planning(settings.PLANNING_FILE)
    items = ""
    for budget in planning.budgets:
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/budgets/{budget.id}/">
                {escape(budget.department.name)} – {escape(budget.period)}
            </a>
            <span class="badge bg-primary">
                {money(budget.get_total_planned())} руб.
            </span>
        </li>
        """

    totals = ""
    for period in sorted({b.period for b in planning.budgets}):
        total = money(planning.get_total_by_period(period))
        totals += f"""
        <p>
            Общая сумма за {escape(period)}:
            <strong>{total} руб.</strong>
        </p>
        """

    content = f"""
    <h1>Бюджеты</h1>
    <ul class="list-group mb-3">{items}</ul>
    {totals}
    """
    return HttpResponse(page("Бюджеты", content))


def budget_detail(request, budget_id):
    planning = load_planning(settings.PLANNING_FILE)
    budget = planning.find_budget_by_id(budget_id)
    if budget is None:
        content = """
        <h1 class="text-danger">Бюджет не найден</h1>
        <a href="/budgets/" class="btn btn-outline-secondary">
            ← к списку бюджетов
        </a>
        """
        return HttpResponse(
            page("Бюджет не найден", content),
            status=404,
        )

    rows = ""
    for item in budget.items:
        rows += f"""
        <tr>
            <td>{escape(item.category)}</td>
            <td class="text-end">{money(item.planned)} руб.</td>
        </tr>
        """
    department = budget.department
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Бюджет №{budget.id}</h5>
            <p class="card-text">
                Подразделение:
                <a href="/departments/{department.id}/">
                    {escape(department.name)}
                </a>
            </p>
            <p class="card-text">
                Руководитель: {escape(department.head)}
            </p>
            <p class="card-text">Период: {escape(budget.period)}</p>
            <table class="table">
                <thead>
                    <tr><th>Статья</th><th class="text-end">План</th></tr>
                </thead>
                <tbody>{rows}</tbody>
                <tfoot>
                    <tr>
                        <th>Итого</th>
                        <th class="text-end">
                            {money(budget.get_total_planned())} руб.
                        </th>
                    </tr>
                </tfoot>
            </table>
            <a href="/budgets/" class="btn btn-outline-secondary">
                ← к списку бюджетов
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Бюджет №{budget.id}", content),
        status=200,
    )
