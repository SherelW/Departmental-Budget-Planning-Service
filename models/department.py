class Department:
    """Подразделение"""

    def __init__(self, name: str, head: str):
        if not name:
            raise ValueError("Название подразделения не может быть пустым")
        if not head:
            raise ValueError("Руководитель не может быть пустым")
        self.name = name
        self.head = head

    def to_dict(self) -> dict:
        return {"name": self.name, "head": self.head}

    @classmethod
    def from_dict(cls, data: dict) -> "Department":
        return cls(name=data["name"], head=data["head"])

    def __repr__(self) -> str:
        return f"Department(name={self.name!r}, head={self.head!r})"