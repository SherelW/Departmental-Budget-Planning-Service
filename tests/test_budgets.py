import pytest
from models import Budget, Department


def _make_department() -> Department:
    return Department("Финансовый отдел", "Иванов И.")


def test_create_budget():
    budget = Budget(_make_department(), "01.09.2026")

    assert budget.department.name == "Финансовый отдел"
    assert budget.period == "01.09.2026"
    assert budget.items == []


def test_empty_period():
    with pytest.raises(ValueError):
        Budget(_make_department(), "")


def test_add_item():
    budget = Budget(_make_department(), "01.09.2026")
    budget.add_item("Зарплата", 20_000)

    assert len(budget.items) == 1
    assert budget.items[0].category == "Зарплата"
    assert budget.items[0].planned == 20_000


def test_total_planned():
    budget = Budget(_make_department(), "01.09.2026")
    budget.add_item("Зарплата", 20_000)
    budget.add_item("Оборудование", 100_000)
    budget.add_item("Командировки", 50_000)

    assert budget.get_total_planned() == 170_000


def test_negative_item():
    budget = Budget(_make_department(), "01.09.2026")
    with pytest.raises(ValueError):
        budget.add_item("Плохая статья", -500)


def test_empty_category():
    budget = Budget(_make_department(), "01.09.2026")
    with pytest.raises(ValueError):
        budget.add_item("", 1000)


def test_budget_to_dict_and_back():
    budget = Budget(_make_department(), "01.09.2026")
    budget.add_item("Зарплата", 20_000)
    budget.add_item("Оборудование", 100_000)

    data = budget.to_dict()
    assert data["period"] == "01.09.2026"
    assert len(data["items"]) == 2

    restored = Budget.from_dict(data)
    assert restored.department.name == "Финансовый отдел"
    assert restored.period == "01.09.2026"
    assert len(restored.items) == 2
    assert restored.items[0].category == "Зарплата"
    assert restored.get_total_planned() == 120_000
