from django.conf import settings
from django.shortcuts import render

from storage import load_planning


def budgets(request):
    planning = load_planning(settings.PLANNING_FILE)

    periods = sorted({b.period for b in planning.budgets})
    period_totals = [
        {"period": p, "total": planning.get_total_by_period(p)}
        for p in periods
    ]

    context = {
        "budgets": planning.budgets,
        "period_totals": period_totals,
    }

    return render(
        request,
        "budgets/budget_list.html",
        context,
    )


def budget_detail(request, budget_id):
    planning = load_planning(settings.PLANNING_FILE)
    budget = planning.find_budget_by_id(budget_id)

    context = {
        "budget": budget,
    }

    return render(
        request,
        "budgets/budget_detail.html",
        context,
        status=404 if budget is None else 200,
    )
