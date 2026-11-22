"""Пересоздать базу данных: схема + перенос данных из JSON.

Запуск из корня проекта:  python -m db.init_db
"""
from db import database, import_json


def main():
    database.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    database.DB_PATH.unlink(missing_ok=True)

    conn = database.get_connection()
    try:
        database.init_schema(conn)
    finally:
        conn.close()

    import_json.main()
    print(f"База данных создана: {database.DB_PATH}")


if __name__ == "__main__":
    main()
