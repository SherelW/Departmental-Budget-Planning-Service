from .department import Department
from .budget_item import BudgetItem


class Budget:
    """Бюджет подразделения на период"""

    def __init__(
        self,
        department: Department,
        period: str,
        id: int | None = None,
    ):
        if not period:
            raise ValueError("Период не может быть пустым")
        self.id = id
        self.department = department
        self.period = period
        self.items: list[BudgetItem] = []

    def add_item(self, category: str, planned: float) -> BudgetItem:
        item = BudgetItem(category, planned)
        self.items.append(item)
        return item

    def get_total_planned(self) -> float:
        return sum(item.planned for item in self.items)

    def to_dict(self) -> dict:
        data = {
            "department": self.department.to_dict(),
            "period": self.period,
            "items": [item.to_dict() for item in self.items],
        }
        if self.id is not None:
            data = {"id": self.id, **data}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        department = Department.from_dict(data["department"])
        budget = cls(
            department=department,
            period=data["period"],
            id=data.get("id"),
        )
        budget.items = [BudgetItem.from_dict(i) for i in data["items"]]
        return budget

    def __repr__(self) -> str:
        return (
            f"Budget(id={self.id}, "
            f"department={self.department.name!r}, "
            f"period={self.period!r}, "
            f"total={self.get_total_planned()}, "
            f"items={len(self.items)})"
        )
