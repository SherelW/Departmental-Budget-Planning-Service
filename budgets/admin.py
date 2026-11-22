from django.contrib import admin

from .models import Budget, BudgetItem


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 1


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("department", "period", "period_start", "period_end")
    list_filter = ("department",)
    inlines = [BudgetItemInline]
