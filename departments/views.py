from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render

from budgets.expressions import sum_planned
from budgets.models import BudgetItem
from departments.models import Department


def departments(request):
    query = request.GET.get("q", "").strip()

    departments_list = Department.objects.all()

    # Поиск по названию или по руководителю (условие «ИЛИ» через Q).
    if query:
        departments_list = departments_list.filter(
            Q(name__icontains=query) | Q(head__icontains=query)
        )

    context = {
        "departments": departments_list.order_by("name"),
        "query": query,
    }

    return render(
        request,
        "departments/department_list.html",
        context,
    )


def department_detail(request, department_id):
    # Если подразделения нет, get_object_or_404() вернёт ответ 404.
    department = get_object_or_404(Department, pk=department_id)

    # Обратная связь: бюджеты подразделения с суммой по статьям.
    budgets_list = (
        department.budgets
        .annotate(total=sum_planned())
        .order_by("period_start")
    )

    # Фильтрация по полю связанной модели: budget__department.
    items = (
        BudgetItem.objects
        .filter(budget__department=department)
        .select_related("budget")
        .order_by("budget__period_start", "-planned")
    )

    total = items.aggregate(total=Sum("planned"))["total"] or 0

    context = {
        "department": department,
        "budgets": budgets_list,
        "items": items,
        "total": total,
    }

    return render(
        request,
        "departments/department_detail.html",
        context,
    )
