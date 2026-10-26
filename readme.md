# Бюджетное планирование подразделений

## Назначение
Приложение для планирования бюджетов подразделений на период.
Консольная версия (ПР3) дополнена веб-интерфейсом на Django (ПР5).

Возможности веб-интерфейса (ПР5):

* просмотр списка подразделений и информации о подразделении;
* просмотр списка бюджетов и статей конкретного бюджета;
* просмотр итоговых сумм по бюджету, подразделению и периоду.

Консольная версия дополнительно умеет создавать данные и сохранять их в JSON.

## Используемые технологии
* Python 3.11+;
* Django 5.2 (LTS) – веб-фреймворк;
* HTML, CSS, Bootstrap 5.3 (CDN) – оформление страниц;
* pytest – тесты, flake8 – проверка качества кода.

## Предметная область
Основные объекты:

* `Department` – подразделение (id, name, head);
* `BudgetItem` – статья бюджета (category, planned);
* `Budget` – бюджет подразделения на период (id, department, period, items);
* `Planning` – набор бюджетов (name, budgets).

Основные методы `Planning`: `add_budget()`, `get_budgets_by_period()`,
`get_budgets_by_department()`, `get_total_by_period()`, `get_departments()`,
`find_department_by_id()`, `find_budget_by_id()` (последние три – ПР5).
Идентификаторы `id` присваиваются автоматически при `add_budget()` и
при загрузке старых JSON без `id`.

## Страницы веб-интерфейса
| URL | View-функция | Назначение |
|-----|--------------|------------|
| `/` | `homepage.views.index` | главная, навигация |
| `/departments/` | `departments.views.departments` | список подразделений |
| `/departments/<int:department_id>/` | `departments.views.department_detail` | карточка подразделения, его бюджеты |
| `/budgets/` | `budgets.views.budgets` | список бюджетов и суммы по периодам |
| `/budgets/<int:budget_id>/` | `budgets.views.budget_detail` | таблица статей бюджета |

Если подразделение или бюджет не найдены, возвращается страница с кодом 404.
Несуществующие адреса обрабатывает `handler404` (`homepage.views.page_not_found`).
Общий HTML-каркас формирует функция `page()` в `homepage/views.py`.

## Структура проекта
```text
budget_planning/
├── manage.py
├── main.py              # консольная версия (ПР3)
├── storage.py           # Storage, load_planning()
├── requirements.txt
├── budgetplan/          # настройки Django-проекта (settings, urls, asgi, wsgi)
├── homepage/            # главная, page(), 404
├── departments/         # страницы подразделений
├── budgets/             # страницы бюджетов
├── models/              # классы предметной области (ПР3)
├── data/planning.json   # данные
└── tests/               # pytest-тесты ПР3
```

## Запуск
```text
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Открыть http://127.0.0.1:8000/

Консольная версия: `python main.py`

## Тестирование и качество кода
```text
pytest -v
python manage.py test
flake8 .
```

## Проверка страницы 404
В `budgetplan/settings.py` временно поставить `DEBUG = False`, открыть
`/nonexistent/`, затем вернуть `DEBUG = True`.

## Текущее состояние и план
Реализовано (ПР5): Django-проект, три приложения, двухуровневая маршрутизация,
view-функции, страницы на Bootstrap, обработка 404, данные из JSON (ПР3).

Планируется: Django ORM и база данных, шаблоны вместо `page()`, формы,
аутентификация, API.
