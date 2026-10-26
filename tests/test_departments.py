import pytest
from models import Department


def test_create_department():
    department = Department("Финансовый отдел", "Иванов И.")
    assert department.name == "Финансовый отдел"
    assert department.head == "Иванов И."


def test_empty_department_name():
    with pytest.raises(ValueError):
        Department("", "Иванов И.")


def test_empty_department_head():
    with pytest.raises(ValueError):
        Department("Финансовый отдел", "")


def test_department_to_dict():
    department = Department("Финансовый отдел", "Иванов И.")
    data = department.to_dict()
    assert data == {"name": "Финансовый отдел", "head": "Иванов И."}


def test_department_from_dict():
    data = {"name": "Финансовый отдел", "head": "Иванов И."}
    department = Department.from_dict(data)
    assert department.name == "Финансовый отдел"
    assert department.head == "Иванов И."


def test_department_id_in_dict():
    department = Department("Финансовый отдел", "Иванов И.", id=3)
    assert department.to_dict()["id"] == 3
    assert Department.from_dict(department.to_dict()).id == 3
