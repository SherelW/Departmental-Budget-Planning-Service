# Бюджетное планирование подразделений

Система планирования бюджетов подразделений на Python с веб-интерфейсом на Django и хранением данных в SQLite.

## 1. Назначение проекта
Приложение хранит подразделения, их бюджеты на период и статьи расходов. Данные просматриваются через веб-интерфейс:
списки, карточки, поиск бюджетов на выбранную дату и статистика. Проект развивается поэтапно:
консольная версия и JSON-хранилище (ПР1–ПР3), веб-интерфейс на Django (ПР5), шаблоны Django (ПР6),
реляционная база SQLite и SQL-запросы (ПР7).

## 2. Используемые технологии
- Python 3, стандартная библиотека `sqlite3`;
- SQLite, язык SQL;
- Django 5.2 (LTS), Django Template Language;
- HTML5, CSS3, JavaScript, Bootstrap 5.3;
- JSON (исходные данные), pytest, flake8, Git.

## 3. Предметная область
Классы предметной области (пакет `models/`, ПР3): `Department`, `BudgetItem`, `Budget`, `Planning`.
Они и консольная версия (`main.py`) сохранены. Веб-интерфейс с ПР7 получает данные из SQLite.

## 4. Структура проекта
```text
budget_planning/
├── budgetplan/              # настройки Django-проекта
├── templates/               # base.html, 404.html, includes/navigation.html
├── homepage/                # главная, статика (css, js, логотип)
├── departments/             # страницы подразделений
├── budgets/                 # страницы бюджетов, поиск на дату, статистика
├── db/
│   ├── __init__.py
│   ├── database.py          # подключение к SQLite, создание схемы
│   ├── import_json.py       # перенос данных из JSON в SQLite
│   └── init_db.py           # пересоздание базы: схема + импорт
├── sql/
│   ├── schema.sql           # создание таблиц
│   └── queries.sql          # SQL-запросы проекта (20 запросов)
├── data/
│   ├── planning.json        # исходные данные (JSON, ПР1–ПР6)
│   └── budget_planning.sqlite   # база данных SQLite
├── models/                  # классы предметной области (ПР3)
├── tests/                   # pytest-тесты
├── main.py                  # консольная версия
├── storage.py               # JSON-хранилище (ПР3)
└── manage.py
```

## 5. Структура базы данных
Для каждой сущности предметной области создана таблица. Первичный ключ каждой таблицы – поле `id`.

**departments** – подразделения

| Поле | Тип | Назначение |
|------|-----|------------|
| id | INTEGER | идентификатор, первичный ключ |
| name | TEXT NOT NULL UNIQUE | название подразделения |
| head | TEXT NOT NULL | руководитель |

**budgets** – бюджеты подразделений на период

| Поле | Тип | Назначение |
|------|-----|------------|
| id | INTEGER | идентификатор, первичный ключ |
| department_id | INTEGER NOT NULL | внешний ключ на `departments.id` |
| period | TEXT NOT NULL | период для показа: `01.09.2026 - 30.09.2026` |
| period_start | TEXT NOT NULL | начало периода, `YYYY-MM-DD` |
| period_end | TEXT NOT NULL | конец периода, `YYYY-MM-DD` |

**budget_items** – статьи бюджета

| Поле | Тип | Назначение |
|------|-----|------------|
| id | INTEGER | идентификатор, первичный ключ |
| budget_id | INTEGER NOT NULL | внешний ключ на `budgets.id` |
| category | TEXT NOT NULL | статья расходов |
| planned | REAL NOT NULL | плановая сумма, `CHECK (planned > 0)` |

Связи: `budgets.department_id → departments.id`, `budget_items.budget_id → budgets.id`.
Одно подразделение имеет несколько бюджетов, один бюджет – несколько статей.
Даты хранятся строками `YYYY-MM-DD`: их можно сравнивать и сортировать средствами SQL (`BETWEEN`, `ORDER BY`).
Поля `NOT NULL` не допускают отсутствия значения; `CHECK` защищает от неположительных сумм.

## 6. Создание и наполнение базы
```text
python -m db.init_db
```
Команда удаляет старый файл базы, создаёт таблицы из `sql/schema.sql` (`CREATE TABLE IF NOT EXISTS`) и переносит данные
из `data/planning.json` скриптом `db/import_json.py`. Отдельно импорт запускается так: `python -m db.import_json`.

- `db/database.py` – `get_connection()` подключается к SQLite и включает `PRAGMA foreign_keys = ON`;
- `db/import_json.py` – `executemany()` с параметрами `?`; период `01.09.2026 - 30.09.2026` разбирается в две ISO-даты;
  порядок импорта: подразделения, бюджеты, статьи (внешние ключи требуют существующих родительских записей);
  при ошибке выполняется `rollback()`.

## 7. SQL-запросы (`sql/queries.sql`)
Всего 20 запросов, каждый проверен в SQLite CLI и с комментарием:

| Вид | Запросы |
|-----|---------|
| Выборка списков (`SELECT`, `ORDER BY`, `DISTINCT`, `LIMIT/OFFSET`) | 1–3 |
| Фильтрация (`WHERE`) | 4–6 |
| Соединение таблиц (`JOIN`, подзапрос `NOT IN`) | 7–10 |
| Агрегатные функции (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`) | 11–13 |
| Группировка (`GROUP BY`) | 14–18 |
| Фильтрация групп (`HAVING`) | 19–20 |

Проверка в консоли: `sqlite3 data/budget_planning.sqlite`.

## 8. Получение данных из SQLite в Django
Путь данных: `SQLite → SQL → sqlite3 → view → context → шаблон → страница`.
В представлениях используется `conn.row_factory = sqlite3.Row`, поэтому поля доступны по именам
(`{{ budget.department_name }}`). Все значения, пришедшие от пользователя или из URL, передаются в запросы параметрами `?`
(`conn.execute(query, [value])`), строки SQL через f-строки не формируются.

## 9. Страницы сайта
| URL | Имя маршрута | Данные из SQLite |
|-----|--------------|------------------|
| `/` | `homepage:index` | – |
| `/departments/` | `departments:list` | список подразделений |
| `/departments/<id>/` | `departments:detail` | подразделение, его бюджеты, статьи, итог |
| `/budgets/` | `budgets:list` | бюджеты с суммами (JOIN + GROUP BY), итоги по периодам |
| `/budgets/<id>/` | `budgets:detail` | бюджет, подразделение, статьи, итог |
| `/budgets/search/?date=YYYY-MM-DD` | `budgets:search` | бюджеты на дату и подразделения без бюджета |
| `/budgets/statistics/?min_total=N` | `budgets:statistics` | агрегаты, группировки, HAVING |

Если объект не найден, страница возвращает статус 404. Неверная дата или число в поиске дают понятное сообщение.
Навигация: Главная | Подразделения | Бюджеты | Статистика; ссылки формируются через `{% url %}`.

## 10. Запуск
```text
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m db.init_db            # если нужно пересоздать базу
python manage.py migrate
python manage.py runserver
```
Адрес: http://127.0.0.1:8000/. Консольная версия: `python main.py` (перезаписывает `data/planning.json`;
после этого выполните `python -m db.init_db`, чтобы обновить базу).

## 11. Тестирование и качество кода
```text
python manage.py check
pytest -v
python manage.py test
flake8 . --extend-exclude=venv
```

## 12. Git
Коммиты ПР7 начинаются с метки `PR7:`:
```text
git commit -m "PR7: add SQLite database and SQL queries"
```

## 13. Текущий этап разработки
На ПР7 данные перенесены из JSON в SQLite:

- создана база `data/budget_planning.sqlite`, таблицы описаны в `sql/schema.sql`;
- данные перенесены скриптом `db/import_json.py`;
- запросы сохранены в `sql/queries.sql`;
- Django-представления получают данные из SQLite через `sqlite3` и параметризованные запросы;
- работают страницы списков, карточек, поиска бюджетов на дату и статистики.

JSON-хранилище, классы `models/` и консольная версия сохранены как предыдущая реализация.
Django ORM на этом этапе не используется.

## 14. Дальнейшее развитие
Подключение базы к Django ORM (модели, миграции), формы создания и редактирования, административная панель,
авторизация, API.
