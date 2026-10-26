from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import money, page
from storage import load_planning


def departments(request):
    planning = load_planning(settings.PLANNING_FILE)
    items = ""
    for department in planning.get_departments():
        items += f"""
        <li class="list-group-item">
            <a href="/departments/{department.id}/">
                {escape(department.name)}
            </a>
            – руководитель {escape(department.head)}
        </li>
        """
    content = f"""
    <h1>Подразделения</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Подразделения", content))


def department_detail(request, department_id):
    planning = load_planning(settings.PLANNING_FILE)
    department = planning.find_department_by_id(department_id)
    if department is None:
        content = """
        <h1 class="text-danger">Подразделение не найдено</h1>
        <a href="/departments/" class="btn btn-outline-secondary">
            ← к списку подразделений
        </a>
        """
        return HttpResponse(
            page("Подразделение не найдено", content),
            status=404,
        )

    rows = ""
    total = 0
    for budget in planning.get_budgets_by_department(department.name):
        total += budget.get_total_planned()
        rows += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/budgets/{budget.id}/">{escape(budget.period)}</a>
            <span class="badge bg-primary">
                {money(budget.get_total_planned())} руб.
            </span>
        </li>
        """
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(department.name)}</h5>
            <p class="card-text">
                <strong>ID:</strong> {department.id}
            </p>
            <p class="card-text">
                <strong>Руководитель:</strong> {escape(department.head)}
            </p>
            <p class="card-text"><strong>Бюджеты:</strong></p>
            <ul class="list-group mb-3">{rows}</ul>
            <p class="card-text">
                <strong>Всего запланировано:</strong>
                {money(total)} руб.
            </p>
            <a href="/departments/" class="btn btn-outline-secondary">
                ← к списку подразделений
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(department.name, content),
        status=200,
    )
