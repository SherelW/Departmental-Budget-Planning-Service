-- ==========================================
-- Бюджетное планирование: структура базы данных
-- ==========================================

-- Подразделения
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    head TEXT NOT NULL
);

-- Бюджеты подразделений на период.
-- period       – период в виде, удобном для показа: "01.09.2026 - 30.09.2026"
-- period_start – начало периода, формат YYYY-MM-DD
-- period_end   – конец периода, формат YYYY-MM-DD
-- Даты в формате YYYY-MM-DD можно сравнивать и сортировать как строки.
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    period TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    CHECK (period_start <= period_end),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Статьи бюджета (строки расходов)
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY,
    budget_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    planned REAL NOT NULL CHECK (planned > 0),
    FOREIGN KEY (budget_id) REFERENCES budgets(id)
);
