import json
from pathlib import Path


class Storage:
    """Хранилище данных в JSON-файле."""

    def __init__(self, filename: str):
        self.filename = Path(filename)

    def save(self, data: list) -> None:

        self.filename.parent.mkdir(parents=True, exist_ok=True)

        raw = [item.to_dict() if hasattr(item, "to_dict") else item for item in data]
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(raw, file, ensure_ascii=False, indent=4)

    def load(self) -> list:
        try:
            with self.filename.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            raise ValueError("Файл содержит некорректный JSON")