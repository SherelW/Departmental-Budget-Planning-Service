# 1. Справочник подразделений
def add_department(name, head):
    """Создание подразделения."""
    department = {"name": name, "head": head}
    print(f"Подразделение добавлено: {department}")
    return department


# 2. Формирование бюджета
def create_budget(department, period, amount):
    """Формирование бюджета подразделения на выбранный период."""
    budget = {
        "department": department["name"],
        "period": period,
        "amount": amount,
        "items": []
    }
    print(f"Бюджет создан: {budget}")
    return budget


#  3. Статьи бюджета
def add_item(budget, category, planned):
    item = {"category": category, "planned": planned}
    budget["items"].append(item)
    print(f"Статья добавлена: {item}")
    return item



dep = add_department("Подразделение финансов", "Иванов И.")

budget = create_budget(dep, "01.09.2026", 1_000_000)

add_item(budget, "Зарплата", 20_000)
print(budget)