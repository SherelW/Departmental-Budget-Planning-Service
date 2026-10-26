import pytest
from models import Department, Planning

PERIOD = "01.09.2026 - 30.09.2026"


def _make_planning() -> Planning:
    planning = Planning("Сентябрь")
    finance = Department("Финансы", "Иванов И.")
    it = Department("IT-отдел", "Петров П.")
    planning.add_budget(finance, PERIOD).add_item("Зарплата", 500_000)
    planning.add_budget(it, PERIOD).add_item("Зарплата", 700_000)
    planning.add_budget(finance, "01.10.2026 - 31.10.2026").add_item(
        "Канцтовары", 10_000
    )
    return planning


def test_empty_name():
    with pytest.raises(ValueError):
        Planning("")


def test_ids_assigned():
    planning = _make_planning()
    assert [b.id for b in planning.budgets] == [1, 2, 3]
    assert [d.id for d in planning.get_departments()] == [1, 2]
    first, third = planning.budgets[0], planning.budgets[2]
    assert first.department.id == third.department.id


def test_total_by_period():
    assert _make_planning().get_total_by_period(PERIOD) == 1_200_000


def test_find_by_id():
    planning = _make_planning()
    assert planning.find_budget_by_id(2).department.name == "IT-отдел"
    assert planning.find_budget_by_id(999) is None
    assert planning.find_department_by_id(1).name == "Финансы"
    assert planning.find_department_by_id(999) is None


def test_dict_roundtrip_keeps_ids():
    planning = _make_planning()
    restored = Planning.from_dict(planning.to_dict())
    assert [b.id for b in restored.budgets] == [1, 2, 3]
    assert len(restored.get_departments()) == 2


def test_from_dict_without_ids():
    data = {
        "name": "Старый формат",
        "budgets": [{
            "department": {"name": "A", "head": "X"},
            "period": "p",
            "items": [],
        }],
    }
    planning = Planning.from_dict(data)
    assert planning.budgets[0].id == 1
    assert planning.budgets[0].department.id == 1
