from django.http import HttpResponse


def page(title, content):
    """Единый HTML-каркас всех страниц проекта."""
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/departments/">Подразделения</a>
        <a class="nav-link" href="/budgets/">Бюджеты</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def money(value):
    """Сумма с пробелами между разрядами: 1570000 -> '1 570 000'."""
    return f"{value:,.0f}".replace(",", " ")


def index(request):
    content = """
    <h1 class="display-4">Бюджетное планирование</h1>
    <p class="lead">Планирование бюджетов подразделений по периодам.</p>
    <p>Основные разделы:</p>
    <a href="/departments/" class="btn btn-primary me-2">Подразделения</a>
    <a href="/budgets/" class="btn btn-secondary">Бюджеты</a>
    """
    return HttpResponse(page("Бюджетное планирование", content))


def page_not_found(request, exception):
    content = """
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
