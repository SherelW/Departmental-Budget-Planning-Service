from .budget import Budget
from .department import Department


class Planning:
    """Планирование бюджетов"""

    def __init__(self, name: str):
        if not name:
            raise ValueError("Название планирования не может быть пустым")
        self.name = name
        self.budgets: list[Budget] = []

    def _assign_ids(self, budget: Budget) -> None:
        """Присвоить id бюджету и подразделению, если их ещё нет."""
        if budget.id is None:
            used = [b.id for b in self.budgets if b.id is not None]
            budget.id = max(used, default=0) + 1

        department = budget.department
        if department.id is not None:
            return
        for other in self.budgets:
            same = other.department.name == department.name
            if other is not budget and same and other.department.id:
                department.id = other.department.id
                return
        used = [
            b.department.id for b in self.budgets
            if b.department.id is not None
        ]
        department.id = max(used, default=0) + 1

    def add_budget(self, department: Department, period: str) -> Budget:
        budget = Budget(department, period)
        self._assign_ids(budget)
        self.budgets.append(budget)
        return budget

    def get_budgets_by_period(self, period: str) -> list[Budget]:
        return [b for b in self.budgets if b.period == period]

    def get_budgets_by_department(self, department_name: str) -> list[Budget]:
        return [
            b for b in self.budgets if b.department.name == department_name
        ]

    def get_total_by_period(self, period: str) -> float:
        return sum(
            b.get_total_planned() for b in self.get_budgets_by_period(period)
        )

    def get_departments(self) -> list[Department]:
        """Уникальные подразделения (по id) в порядке появления."""
        result: dict[int, Department] = {}
        for budget in self.budgets:
            result.setdefault(budget.department.id, budget.department)
        return list(result.values())

    def find_department_by_id(self, department_id: int) -> Department | None:
        for department in self.get_departments():
            if department.id == department_id:
                return department
        return None

    def find_budget_by_id(self, budget_id: int) -> Budget | None:
        for budget in self.budgets:
            if budget.id == budget_id:
                return budget
        return None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "budgets": [b.to_dict() for b in self.budgets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Planning":
        planning = cls(name=data["name"])
        planning.budgets = [Budget.from_dict(b) for b in data["budgets"]]
        for budget in planning.budgets:
            planning._assign_ids(budget)
        return planning

    def __repr__(self) -> str:
        return (
            f"Planning(name={self.name!r}, "
            f"budgets_count={len(self.budgets)})"
        )
