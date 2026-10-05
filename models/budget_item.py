class BudgetItem:
    """Статья бюджета"""

    def __init__(self, category: str, planned: float):
        if not category:
            raise ValueError("Категория (статья) не может быть пустой")
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