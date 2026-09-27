from add_department import Department


class BudgetItem:

    def __init__(self, category: str, planned: float):
        if not category:
            raise ValueError("Категория не может быть пустой")
        if planned <= 0:
            raise ValueError("Плановая сумма должна быть больше 0")
        self.category = category
        self.planned = planned

    def to_dict(self) -> dict:
        return {"category": self.category, "planned": self.planned}

    @classmethod
    def from_dict(cls, data: dict) -> "BudgetItem":
        return cls(category=data["category"], planned=data["planned"])

    def __repr__(self) -> str:
        return f"BudgetItem(category={self.category!r}, planned={self.planned})"


class Budget:

    def __init__(self, department: Department, period: str, amount: float):
        if amount <= 0:
            raise ValueError("Сумма бюджета должна быть больше 0")
        self.department = department
        self.period = period
        self.amount = amount
        self.items: list[BudgetItem] = []

    def add_item(self, category: str, planned: float) -> BudgetItem:
        item = BudgetItem(category, planned)
        self.items.append(item)
        return item

    def get_total_planned(self) -> float:
        return sum(item.planned for item in self.items)

    def to_dict(self) -> dict:
        return {
            "department": self.department.to_dict(),
            "period": self.period,
            "amount": self.amount,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        department = Department.from_dict(data["department"])
        budget = cls(department=department, period=data["period"], amount=data["amount"])
        budget.items = [BudgetItem.from_dict(item) for item in data["items"]]
        return budget

    def __repr__(self) -> str:
        return (
            f"Budget(department={self.department.name!r}, "
            f"period={self.period!r}, amount={self.amount}, "
            f"items_count={len(self.items)})"
        )