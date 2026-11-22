# Бюджетное планирование подразделений

Система планирования бюджетов подразделений на Python и Django. Данные хранятся в базе SQLite
и обрабатываются через Django ORM.

## 1. Назначение проекта
Приложение хранит подразделения, их бюджеты на период и статьи расходов. Через веб-интерфейс можно просматривать списки
и карточки, искать, фильтровать, сортировать бюджеты, смотреть бюджеты на выбранную дату и статистику.

Этапы развития проекта: консольная версия и JSON (ПР1–ПР3), веб-интерфейс на Django (ПР5), шаблоны (ПР6),
база SQLite и SQL-запросы (ПР7), **Django ORM и модели (ПР9)**.

## 2. Используемые технологии
- Python 3, Django 5.2 (LTS), Django ORM и миграции;
- SQLite (файл `db.sqlite3` Django и исходная база ПР7 `data/budget_planning.sqlite`);
- Django Template Language, HTML5, CSS3, JavaScript, Bootstrap 5.3;
- pytest, flake8, Git.

## 3. Модели Django
Модели описаны в `models.py` приложений. Корневой пакет `models/` (классы ПР3) – это другое: он остаётся
как предыдущая реализация консольной версии.

| Модель | Приложение | Таблица | Назначение |
|--------|------------|---------|------------|
| `Department` | `departments` | `departments_department` | подразделение |
| `Budget` | `budgets` | `budgets_budget` | бюджет подразделения на период |
| `BudgetItem` | `budgets` | `budgets_budgetitem` | статья бюджета |

**Department:** `name` (CharField, unique), `head` (CharField). Сортировка по умолчанию – по названию.

**Budget:** `department` (ForeignKey → Department, `on_delete=PROTECT`, `related_name="budgets"`), `period` (CharField),
`period_start`, `period_end` (DateField). Ограничение `CheckConstraint`: начало периода не позже конца.
Метод `get_total_planned()` – сумма статей бюджета.

**BudgetItem:** `budget` (ForeignKey → Budget, `on_delete=CASCADE`, `related_name="items"`), `category` (CharField),
`planned` (DecimalField). Ограничение: `planned > 0`.

Связи: одно подразделение – много бюджетов, один бюджет – много статей.
Подразделение с бюджетами удалить нельзя (`PROTECT`), при удалении бюджета его статьи удаляются (`CASCADE`).
Деньги хранятся в `DecimalField`, а не в `float`, чтобы не накапливалась погрешность.

## 4. Миграции
```text
python manage.py makemigrations
python manage.py migrate
```
Миграции приложений лежат в `departments/migrations/` и `budgets/migrations/` и хранятся в Git.
Просмотр SQL миграции: `python manage.py sqlmigrate budgets 0001`.

## 5. Перенос данных из базы ПР7
Источник – `data/budget_planning.sqlite` (ПР7), приёмник – база Django `db.sqlite3`.
```text
python db/inspect_source_db.py          # изучить исходную базу (только чтение)
python db/import_sqlite_to_orm.py       # перенести данные через ORM
```
Скрипт переноса: читает исходную базу через `sqlite3`, создаёт объекты через `update_or_create()` в одной транзакции
(`transaction.atomic`), сохраняет идентификаторы, превращает строки дат в `date`, суммы в `Decimal`.
Порядок: подразделения → бюджеты → статьи (внешние ключи). Повторный запуск безопасен.
Исходную базу желательно скопировать перед работой: `cp data/budget_planning.sqlite data/budget_planning_backup.sqlite`.

## 6. Страницы сайта
| URL | Что делает (ORM) |
|-----|------------------|
| `/` | главная |
| `/departments/?q=` | список подразделений, поиск по названию или руководителю (`Q`, `icontains`) |
| `/departments/<id>/` | подразделение (`get_object_or_404`), его бюджеты (`related_name`), статьи (`filter(budget__department=...)`) |
| `/budgets/` | фильтры (дата, подразделение, поиск), сортировка, пагинация (3 на страницу), итоги по периодам |
| `/budgets/<id>/` | бюджет с подразделением (`select_related`), сумма (`annotate`), статьи |
| `/budgets/search/?date=` | бюджеты на дату и подразделения без бюджета (`exclude(pk__in=...)`) |
| `/budgets/statistics/?min_total=` | `aggregate`, `annotate`, `Count`, `Sum`, `values`, `HAVING` через `filter` по агрегату |

Параметры `/budgets/`: `date=YYYY-MM-DD`, `department=<id>`, `q=<текст>`, `sort=period|department|total`, `page=<номер>`.
Некорректные значения не вызывают ошибок: неверная дата выводит сообщение, неверный идентификатор игнорируется,
неизвестное поле сортировки заменяется сортировкой по периоду, неверный номер страницы открывает первую страницу.

## 7. Используемые ORM-выражения
- получение: `all()`, `get_object_or_404()`, `count()`;
- фильтрация: `filter()` по одному и нескольким условиям, по полю связанной модели, `exclude()`, `__lte`, `__gte`, `__gt`;
- поиск: `icontains` (одно поле), `Q(...) | Q(...)` (несколько полей);
- сортировка: `order_by()` по нескольким полям, по полю связанной модели, по аннотации, по убыванию;
- связи: `select_related()`, обратные связи `department.budgets` и `budget.items`;
- агрегирование: `aggregate(Sum, Avg, Min, Max)`, `annotate(Count, Sum)`, `Coalesce`, `values()`, `F()`;
- пагинация: `Paginator`, `get_page()`; срез `[:3]`.

Особенность SQLite: `icontains` не различает регистр только для латинских букв. Для кириллицы поиск «отдел» не найдёт
«Отдел», вводите текст в том же регистре, что в названии.

## 8. Структура проекта
```text
budget_planning/
├── budgetplan/          # настройки проекта
├── templates/           # base.html, 404.html, includes/
├── homepage/            # главная, статика, Django-тесты страниц
├── departments/         # models.py, views.py, admin.py, шаблоны
├── budgets/             # models.py, expressions.py, views.py, admin.py, шаблоны
├── db/                  # скрипты ПР7 и переноса данных в ORM (ПР9)
├── sql/                 # schema.sql, queries.sql (ПР7)
├── data/                # planning.json, budget_planning.sqlite
├── models/              # классы предметной области (ПР3)
├── tests/               # pytest-тесты
├── main.py, storage.py  # консольная версия
└── manage.py
```

## 9. Запуск
```text
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python db/import_sqlite_to_orm.py
python manage.py runserver
```
Адрес: http://127.0.0.1:8000/. Администрирование: `python manage.py createsuperuser`, затем http://127.0.0.1:8000/admin/.

## 10. Проверка
```text
python manage.py check
python manage.py test
pytest -v
flake8 . --extend-exclude=venv
```
Django-тесты создают собственные данные в тестовой базе и не зависят от `db.sqlite3`.

## 11. Git
Коммиты ПР9 начинаются с метки `PR9:`. Файл `db.sqlite3` в репозиторий не добавляется (он в `.gitignore`).
Файлы миграций в репозиторий добавляются.

## 12. Текущее состояние и дальнейшее развитие
Реализовано: Django-модели и связи, миграции, перенос данных из SQLite, ORM-запросы на всех страницах,
фильтрация, поиск, сортировка, пагинация, статистика, админ-панель.
Планируется: формы Django, создание и редактирование объектов через сайт, авторизация, API.
