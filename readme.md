# Бюджетное планирование подразделений

Система планирования бюджетов подразделений на Python с веб-интерфейсом на Django.

## 1. Назначение проекта
Приложение позволяет хранить сведения о подразделениях и их бюджетах на период, распределять средства по статьям
расходов и просматривать итоги через веб-интерфейс Django. Проект развивается поэтапно: консольная версия (ПР3)
дополнена веб-интерфейсом (ПР5), а на ПР6 веб-часть переведена на систему шаблонов Django.

## 2. Используемые технологии
- Python 3;
- Django 5.2 (LTS);
- Django Template Language (DTL);
- HTML5, CSS3, JavaScript;
- Bootstrap 5.3;
- JSON для хранения данных;
- Git, pytest, flake8.

## 3. Предметная область
- `Department` – подразделение (id, name, head);
- `BudgetItem` – статья бюджета (category, planned);
- `Budget` – бюджет подразделения на период (id, department, period, items);
- `Planning` – набор бюджетов; поиск по id, суммы по периодам и подразделениям.

Для предметной области реализованы собственные Python-классы (пакет `models/`).
Данные хранятся в `data/planning.json`. Django ORM и база данных пока не используются.

## 4. Структура проекта
```text
budget_planning/
├── budgetplan/              # настройки Django-проекта
│   ├── settings.py
│   └── urls.py
├── templates/               # шаблоны уровня проекта
│   ├── base.html
│   ├── 404.html
│   └── includes/
│       └── navigation.html
├── homepage/
│   ├── static/homepage/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/logo.png
│   ├── templates/homepage/index.html
│   ├── urls.py
│   └── views.py
├── departments/
│   ├── templates/departments/
│   │   ├── department_list.html
│   │   ├── department_detail.html
│   │   └── includes/department_card.html
│   ├── urls.py
│   └── views.py
├── budgets/
│   ├── templates/budgets/
│   │   ├── budget_list.html
│   │   ├── budget_detail.html
│   │   └── includes/budget_status.html
│   ├── urls.py
│   └── views.py
├── models/                  # классы предметной области (ПР3)
├── data/planning.json
├── tests/                   # pytest-тесты
├── main.py                  # консольная версия
├── storage.py               # Storage, load_planning()
└── manage.py
```

## 5. Веб-интерфейс
| URL | Имя маршрута | Страница |
|-----|--------------|----------|
| `/` | `homepage:index` | главная страница |
| `/departments/` | `departments:list` | список подразделений |
| `/departments/<id>/` | `departments:detail` | страница подразделения |
| `/budgets/` | `budgets:list` | список бюджетов |
| `/budgets/<id>/` | `budgets:detail` | страница бюджета со статьями |

HTML в Python-коде представлений больше не формируется, функция `page()` из ПР5 удалена.
Представления загружают данные, готовят контекст и вызывают `render()`.
Если объект не найден, страница отображает сообщение и возвращает статус 404
(`status=404 if obj is None else 200`). Неизвестные адреса обрабатывает `handler404` и шаблон `templates/404.html`.

## 6. Django Template Language
- **Базовый шаблон** `templates/base.html`: структура страницы, Bootstrap, собственный CSS, логотип, навигация,
  подвал, JavaScript. Блоки: `{% block title %}` и `{% block content %}`.
- **Наследование**: дочерние шаблоны начинаются с `{% extends "base.html" %}`.
- **Включаемые шаблоны** `{% include %}`: навигация (`includes/navigation.html`), карточка подразделения
  (`departments/includes/department_card.html`), статус бюджета (`budgets/includes/budget_status.html`).
- **Контекст**: например, `context = {"budgets": planning.budgets}` во view и `{% for budget in budgets %}` в шаблоне.
- **Циклы и условия**: `{% for %}`, `{% empty %}` для пустых коллекций, `{% if %}` для состояний («бюджет найден / не найден»,
  «есть статьи / нет статей»).

## 7. Фильтры шаблонов
- `{{ departments|length }}` – количество подразделений;
- `{{ department.name|default:"Без названия" }}` – значение по умолчанию;
- `{{ item.planned|floatformat:"0g" }}` – суммы с разделителями разрядов.

Фильтры используются только для представления данных, бизнес-логика остаётся в Python.

## 8. URL-маршрутизация
В `urls.py` каждого приложения задан `app_name`, ссылки формируются через `{% url %}`:
```text
{% url 'homepage:index' %}
{% url 'departments:list' %}
{% url 'departments:detail' department.id %}
{% url 'budgets:list' %}
{% url 'budgets:detail' budget.id %}
```

## 9. Статические файлы
Каталог `homepage/static/homepage/`: `css/style.css` (собственные стили карточек, статуса и логотипа),
`js/main.js` (выводит текущий год в подвале), `img/logo.png` (логотип).
В шаблонах: `{% load static %}` и `{% static 'homepage/css/style.css' %}`.
Bootstrap подключён для базовой вёрстки и не заменяет собственные стили проекта.

## 10. Хранение данных
Данные хранятся в `data/planning.json`. Загрузка выполняется функцией `load_planning()` из `storage.py`,
которая превращает JSON в объекты `Planning`, `Budget`, `Department`, `BudgetItem`.
Django ORM, формы и база данных на текущем этапе не используются.

## 11. Запуск
```text
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Адрес: http://127.0.0.1:8000/

Консольная версия: `python main.py`

## 12. Тестирование и качество кода
```text
python manage.py check
pytest -v
python manage.py test
flake8 . --extend-exclude=venv
```

## 13. Git
Коммиты ПР6 начинаются с метки `PR6:`:
```text
git commit -m "PR6: add Django templates and static files"
```

## 14. Текущее состояние проекта
Реализовано: предметные классы, консольный интерфейс, хранение в JSON, Django-проект с тремя приложениями,
шаблонный интерфейс (base.html, extends, block, include), контекст, циклы и условия, фильтры,
именованные URL и пространства имён, статические CSS, JavaScript и изображение.

Не реализовано: формы Django, модели Django ORM и работа с базой данных.

## 15. Дальнейшее развитие
Переход от JSON к базе данных и Django ORM, формы Django, операции создания, изменения и удаления объектов,
пользователи и авторизация, API.
