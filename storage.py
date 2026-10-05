import json
from pathlib import Path


class Storage:
    def __init__(self, filename: str):
        self.filename = Path(filename)

    def save(self, obj) -> None:
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        data = obj.to_dict() if hasattr(obj, "to_dict") else obj
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load(self) -> dict:
        try:
            with self.filename.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            raise ValueError("Файл содержит некорректный JSON")