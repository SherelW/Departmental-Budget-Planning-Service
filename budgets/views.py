from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Max, Min, Sum
from django.shortcuts import get_object_or_404, render

from budgets.expressions import sum_planned
from budgets.models import Budget, BudgetItem
from departments.models import Department

PAGE_SIZE = 3
DEFAULT_MIN_TOTAL = Decimal("600000")
LARGE_ITEM = Decimal("200000")
MAX_AMOUNT = Decimal("999999999999")

# Допустимые значения параметра sort и соответствующие поля сортировки.
# Произвольное значение из адреса в order_by() не передаётся.
SORT_FIELDS = {
    "period": "period_start",
    "department": "department__name",
    "total": "-total",
}


def parse_date(text):
    """Дата из строки YYYY-MM-DD или None, если формат неверный."""
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_id(text):
    """Целое число из строки или None, если это не идентификатор."""
    if text.isascii() and text.isdigit() and len(text) <= 9:
        return int(text)
    return None


def parse_amount(text):
    """Неотрицательная сумма из строки или None, если значение неверное."""
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0 or amount > MAX_AMOUNT:
        return None
    return amount


def budgets(request):
    date_text = request.GET.get("date", "").strip()
    department_text = request.GET.get("department", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "period")
    error = None

    budgets_data = Budget.objects.all()

    # Фильтр по дате: бюджеты, действующие на выбранную дату.
    if date_text:
        selected_date = parse_date(date_text)
        if selected_date is None:
            error = "Укажите корректную дату."
        else:
            budgets_data = budgets_data.filter(
                period_start__lte=selected_date,
                period_end__gte=selected_date,
            )

    # Фильтр по подразделению (внешний ключ).
    department_id = parse_id(department_text)
    if department_id is not None:
        budgets_data = budgets_data.filter(department_id=department_id)

    # Поиск по названию подразделения: поле связанной модели.
    if query:
        budgets_data = budgets_data.filter(
            department__name__icontains=query
        )

    # Сортировка по разрешённому полю; неизвестное значение – по периоду.
    if sort not in SORT_FIELDS:
        sort = "period"

    budgets_data = (
        budgets_data
        .annotate(
            department_name=F("department__name"),
            total=sum_planned(),
        )
        .order_by(SORT_FIELDS[sort], "id")
        .values(
            "id",
            "period",
            "period_start",
            "department_name",
            "total",
        )
    )

    # Постраничный вывод применяется после фильтрации и сортировки.
    paginator = Paginator(budgets_data, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Итоги по периодам (группировка по полю period).
    period_totals = (
        Budget.objects
        .values("period")
        .annotate(
            total=Sum("items__planned"),
            first_start=Min("period_start"),
        )
        .filter(total__isnull=False)
        .order_by("first_start")
    )

    context = {
        "budgets": page_obj,
        "page_obj": page_obj,
        "period_totals": period_totals,
        "departments": Department.objects.order_by("name"),
        "date": date_text,
        "selected_department": department_text,
        "query": query,
        "sort": sort,
        "error": error,
    }

    return render(
        request,
        "budgets/budget_list.html",
        context,
    )


def budget_detail(request, budget_id):
    # select_related() загружает подразделение тем же запросом,
    # annotate() добавляет итоговую сумму по статьям.
    budget = get_object_or_404(
        Budget.objects
        .select_related("department")
        .annotate(total=sum_planned()),
        pk=budget_id,
    )

    # Обратная связь: статьи бюджета.
    items = budget.items.order_by("-planned", "category")

    context = {
        "budget": budget,
        "items": items,
    }

    return render(
        request,
        "budgets/budget_detail.html",
        context,
    )


def budget_search(request):
    date_text = request.GET.get("date", "").strip()
    error = None
    searched = False
    budgets_on_date = []
    free_departments = []

    if date_text:
        selected_date = parse_date(date_text)
        if selected_date is None:
            error = "Некорректная дата. Выберите дату в календаре."
        else:
            searched = True

            # Бюджеты, действующие на выбранную дату.
            active = Budget.objects.filter(
                period_start__lte=selected_date,
                period_end__gte=selected_date,
            )
            budgets_on_date = (
                active
                .annotate(
                    department_name=F("department__name"),
                    department_head=F("department__head"),
                )
                .values(
                    "id",
                    "period",
                    "department_name",
                    "department_head",
                )
                .order_by("department_name")
            )

            # Подразделения, у которых нет бюджета на эту дату.
            busy_ids = active.values_list("department_id", flat=True)
            free_departments = (
                Department.objects
                .exclude(pk__in=busy_ids)
                .order_by("name")
            )

    periods = (
        Budget.objects
        .values("period", "period_start")
        .distinct()
        .order_by("period_start")
    )

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
    min_total_text = request.GET.get("min_total", "").strip()
    if min_total_text:
        parsed = parse_amount(min_total_text)
        if parsed is None:
            error = "Минимальная сумма должна быть неотрицательным числом."
        else:
            min_total = parsed

    # Количество бюджетов и сводные показатели по статьям.
    budgets_count = Budget.objects.count()
    totals = BudgetItem.objects.aggregate(
        total_planned=Sum("planned"),
        avg_item=Avg("planned"),
        min_item=Min("planned"),
        max_item=Max("planned"),
    )
    totals = {key: value or 0 for key, value in totals.items()}

    # Подразделения без бюджетов тоже попадают в статистику.
    by_department = (
        Department.objects
        .annotate(
            department_name=F("name"),
            budgets_count=Count("budgets", distinct=True),
            total=sum_planned("budgets__items__planned"),
        )
        .values("department_name", "budgets_count", "total")
        .order_by("-total", "department_name")
    )

    by_category = (
        BudgetItem.objects
        .values("category")
        .annotate(
            items_count=Count("pk"),
            total=Sum("planned"),
        )
        .order_by("-total", "category")
    )

    # Срез QuerySet: три самые крупные статьи.
    top_items = (
        BudgetItem.objects
        .order_by("-planned", "category")
        .values("category", "planned")[:3]
    )

    large_items = (
        BudgetItem.objects
        .filter(planned__gte=LARGE_ITEM)
        .order_by("-planned", "category")
        .values("category", "planned")
    )

    # Фильтрация по результату агрегации (HAVING в SQL).
    large_budgets = (
        Budget.objects
        .annotate(
            department_name=F("department__name"),
            total=Sum("items__planned"),
        )
        .filter(total__gte=min_total)
        .values("id", "period", "department_name", "total")
        .order_by("-total", "id")
    )

    busy_departments = (
        Department.objects
        .annotate(
            department_name=F("name"),
            budgets_count=Count("budgets"),
        )
        .filter(budgets_count__gt=1)
        .values("department_name", "budgets_count")
        .order_by("-budgets_count", "department_name")
    )

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
