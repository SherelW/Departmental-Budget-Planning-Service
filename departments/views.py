from django.conf import settings
from django.shortcuts import render

from storage import load_planning


def departments(request):
    planning = load_planning(settings.PLANNING_FILE)

    context = {
        "departments": planning.get_departments(),
    }

    return render(
        request,
        "departments/department_list.html",
        context,
    )


def department_detail(request, department_id):
    planning = load_planning(settings.PLANNING_FILE)
    department = planning.find_department_by_id(department_id)

    budgets_list = []
    total = 0
    if department is not None:
        budgets_list = planning.get_budgets_by_department(department.name)
        total = sum(b.get_total_planned() for b in budgets_list)

    context = {
        "department": department,
        "budgets": budgets_list,
        "total": total,
    }

    return render(
        request,
        "departments/department_detail.html",
        context,
        status=404 if department is None else 200,
    )
