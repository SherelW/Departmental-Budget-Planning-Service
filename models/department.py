class Department:
    """Подразделение"""

    def __init__(self, name: str, head: str, id: int | None = None):
        if not name:
            raise ValueError("Название подразделения не может быть пустым")
        if not head:
            raise ValueError("Руководитель не может быть пустым")
        self.id = id
        self.name = name
        self.head = head

    def to_dict(self) -> dict:
        data = {"name": self.name, "head": self.head}
        if self.id is not None:
            data = {"id": self.id, **data}
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Department":
        return cls(
            name=data["name"],
            head=data["head"],
            id=data.get("id"),
        )

    def __repr__(self) -> str:
        return (
            f"Department(id={self.id}, name={self.name!r}, "
            f"head={self.head!r})"
        )
