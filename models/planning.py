from .budget import Budget
from .department import Department


class Planning:
    """Планирование бюджетов"""

    def __init__(self, name: str):
        if not name:
            raise ValueError("Название планирования не может быть пустым")
        self.name = name
        self.budgets: list[Budget] = []

    def add_budget(self, department: Department, period: str) -> Budget:
        budget = Budget(department, period)
        self.budgets.append(budget)
        return budget

    def get_budgets_by_period(self, period: str) -> list[Budget]:
        return [b for b in self.budgets if b.period == period]

    def get_budgets_by_department(self, department_name: str) -> list[Budget]:
        return [b for b in self.budgets if b.department.name == department_name]

    def get_total_by_period(self, period: str) -> float:
        return sum(b.get_total_planned() for b in self.get_budgets_by_period(period))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "budgets": [b.to_dict() for b in self.budgets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Planning":
        planning = cls(name=data["name"])
        planning.budgets = [Budget.from_dict(b) for b in data["budgets"]]
        return planning

    def __repr__(self) -> str:
        return f"Planning(name={self.name!r}, budgets_count={len(self.budgets)})"