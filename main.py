from add_department import Department
from create_budget import Budget
from storage import Storage


def main():
    department = Department("Подразделение финансов", "Иванов И.")

    budget = Budget(department, "01.09.2026", 1_000_000)

    budget.add_item("Зарплата", 20_000)
    budget.add_item("Оборудование", 100_000)
    budget.add_item("Командировки", 50_000)

    print("Подразделение:")
    print(department)
    print("\nБюджет:")
    print(budget)
    print(f"\nВсего запланировано: {budget.get_total_planned()} руб.")

    storage = Storage("data/budgets.json")
    storage.save([budget])
    print("\nДанные сохранены в data/budgets.json")

    loaded_raw = storage.load()
    loaded_budgets = [Budget.from_dict(item) for item in loaded_raw]
    print(f"\nЗагружено бюджетов: {len(loaded_budgets)}")
    print(loaded_budgets[0])


if __name__ == "__main__":
    main()