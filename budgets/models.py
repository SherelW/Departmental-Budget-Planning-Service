from django.db import models
from django.db.models import F, Q, Sum

from departments.models import Department


class Budget(models.Model):
    """Бюджет подразделения на период."""

    # Подразделение нельзя удалить, пока у него есть бюджеты.
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="budgets",
        verbose_name="Подразделение",
    )
    # Период в виде для показа: "01.09.2026 - 30.09.2026".
    period = models.CharField(
        max_length=100,
        verbose_name="Период",
    )
    # Границы периода хранятся датами: по ним ищем бюджет на дату.
    period_start = models.DateField(
        verbose_name="Начало периода",
    )
    period_end = models.DateField(
        verbose_name="Конец периода",
    )

    def get_total_planned(self):
        """Сумма плановых значений всех статей бюджета."""
        total = self.items.aggregate(total=Sum("planned"))["total"]
        return total or 0

    def __str__(self):
        return f"{self.department} — {self.period}"

    class Meta:
        ordering = ["period_start", "pk"]
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджеты"
        constraints = [
            models.CheckConstraint(
                condition=Q(period_start__lte=F("period_end")),
                name="budget_period_start_lte_end",
            ),
        ]


class BudgetItem(models.Model):
    """Статья бюджета."""

    # Статья не существует без бюджета: при удалении бюджета удаляется.
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Бюджет",
    )
    category = models.CharField(
        max_length=200,
        verbose_name="Статья расходов",
    )
    planned = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Плановая сумма",
    )

    def __str__(self):
        return f"{self.category}: {self.planned}"

    class Meta:
        ordering = ["pk"]
        verbose_name = "Статья бюджета"
        verbose_name_plural = "Статьи бюджета"
        constraints = [
            models.CheckConstraint(
                condition=Q(planned__gt=0),
                name="budgetitem_planned_positive",
            ),
        ]
