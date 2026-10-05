from models import Department, Budget, BudgetItem, Planning
from storage import Storage

def main():

    planning = Planning("Бюджет на сентябрь 2026")

    finance = Department("Подразделение финансов", "Иванов И.")
    it = Department("IT-отдел", "Петров П.")

    budget_finance = planning.add_budget(finance, "01.09.2026 - 30.09.2026")
    budget_finance.add_item("Зарплата", 500_000)
    budget_finance.add_item("Командировки", 50_000)
    budget_finance.add_item("Канцтовары", 20_000)

    budget_it = planning.add_budget(it, "01.09.2026 - 30.09.2026")
    budget_it.add_item("Зарплата", 700_000)
    budget_it.add_item("Оборудование", 300_000)

    print("=== Планирование ===")
    print(planning)
    print()

    for budget in planning.budgets:
        print(f"Подразделение: {budget.department.name}")
        print(f"Руководитель: {budget.department.head}")
        print(f"Период: {budget.period}")
        print("Статьи:")
        for item in budget.items:
            print(f"  - {item.category}: {item.planned} руб.")
        print(f"Итого по подразделению: {budget.get_total_planned()} руб.")
        print("-" * 40)

    print(f"\nОбщая сумма за период: {planning.get_total_by_period('01.09.2026 - 30.09.2026')} руб.")

    storage = Storage("data/planning.json")
    storage.save(planning)
    print("\nДанные сохранены в data/planning.json")

    loaded_data = storage.load()
    loaded_planning = Planning.from_dict(loaded_data)
    print(f"\nЗагружено: {loaded_planning}")
    print(f"Количество бюджетов: {len(loaded_planning.budgets)}")


if __name__ == "__main__":
    main()