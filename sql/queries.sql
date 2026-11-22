-- ==========================================
-- Бюджетное планирование: SQL-запросы проекта
-- Проверка: sqlite3 data/budget_planning.sqlite
-- В запросах ниже стоят конкретные значения для проверки в SQLite CLI;
-- в веб-приложении они передаются параметрами (?) из Django.
-- ==========================================


-- ---------- Выборка списков (SELECT ... ORDER BY) ----------

-- 1. Список подразделений (страница «Подразделения»)
SELECT
    id,
    name,
    head
FROM departments
ORDER BY name;

-- 2. Список периодов, на которые есть бюджеты (страница «Бюджеты на дату»)
SELECT DISTINCT
    period,
    period_start
FROM budgets
ORDER BY period_start;

-- 3. Три самые крупные статьи расходов: LIMIT и OFFSET (страница «Статистика»)
SELECT
    category,
    planned
FROM budget_items
ORDER BY planned DESC, category
LIMIT 3 OFFSET 0;


-- ---------- Фильтрация (WHERE) ----------

-- 4. Подразделение по идентификатору (страница подразделения, 404 при пустом результате)
SELECT
    id,
    name,
    head
FROM departments
WHERE id = 1;

-- 5. Статьи конкретного бюджета (страница бюджета)
SELECT
    category,
    planned
FROM budget_items
WHERE budget_id = 1
ORDER BY planned DESC;

-- 6. Крупные статьи расходов: от 200 000 (страница «Статистика»)
SELECT
    category,
    planned
FROM budget_items
WHERE planned >= 200000
ORDER BY planned DESC;


-- ---------- Соединение таблиц (JOIN) ----------

-- 7. Бюджет с данными подразделения и итоговой суммой (страница бюджета)
SELECT
    b.id,
    b.period,
    d.id AS department_id,
    d.name AS department_name,
    d.head AS department_head,
    (
        SELECT COALESCE(SUM(bi.planned), 0)
        FROM budget_items AS bi
        WHERE bi.budget_id = b.id
    ) AS total
FROM budgets AS b
JOIN departments AS d
    ON b.department_id = d.id
WHERE b.id = 1;

-- 8. Все статьи подразделения с периодом бюджета (страница подразделения)
SELECT
    b.id AS budget_id,
    b.period,
    bi.category,
    bi.planned
FROM budget_items AS bi
JOIN budgets AS b
    ON bi.budget_id = b.id
WHERE b.department_id = 1
ORDER BY b.period_start, bi.planned DESC;

-- 9. Бюджеты, действующие на выбранную дату (страница «Бюджеты на дату»)
SELECT
    b.id,
    b.period,
    d.name AS department_name,
    d.head AS department_head
FROM budgets AS b
JOIN departments AS d
    ON b.department_id = d.id
WHERE '2026-09-15' BETWEEN b.period_start AND b.period_end
ORDER BY d.name;

-- 10. Подразделения без бюджета на выбранную дату: подзапрос NOT IN
SELECT
    id,
    name,
    head
FROM departments
WHERE id NOT IN (
    SELECT department_id
    FROM budgets
    WHERE '2026-10-15' BETWEEN period_start AND period_end
)
ORDER BY name;


-- ---------- Агрегатные функции (COUNT, SUM, AVG, MIN, MAX) ----------

-- 11. Количество бюджетов (страница «Статистика»)
SELECT
    COUNT(*) AS budgets_count
FROM budgets;

-- 12. Общая, средняя, наименьшая и наибольшая сумма по статьям
SELECT
    COALESCE(SUM(planned), 0) AS total_planned,
    COALESCE(AVG(planned), 0) AS avg_item,
    COALESCE(MIN(planned), 0) AS min_item,
    COALESCE(MAX(planned), 0) AS max_item
FROM budget_items;

-- 13. Общая сумма по всем бюджетам подразделения (страница подразделения)
SELECT
    COALESCE(SUM(bi.planned), 0) AS total
FROM budget_items AS bi
JOIN budgets AS b
    ON bi.budget_id = b.id
WHERE b.department_id = 1;


-- ---------- Группировка (GROUP BY) ----------

-- 14. Итоговая сумма по каждому бюджету; бюджет без статей получает 0 (страница «Бюджеты»)
SELECT
    b.id,
    b.period,
    d.name AS department_name,
    COALESCE(SUM(bi.planned), 0) AS total
FROM budgets AS b
JOIN departments AS d
    ON b.department_id = d.id
LEFT JOIN budget_items AS bi
    ON bi.budget_id = b.id
GROUP BY b.id, b.period, d.name
ORDER BY b.period_start, d.name;

-- 15. Итоги по периодам (страница «Бюджеты»)
SELECT
    b.period,
    SUM(bi.planned) AS total
FROM budgets AS b
JOIN budget_items AS bi
    ON bi.budget_id = b.id
GROUP BY b.period
ORDER BY MIN(b.period_start);

-- 16. Бюджеты подразделения с суммами (страница подразделения)
SELECT
    b.id,
    b.period,
    COALESCE(SUM(bi.planned), 0) AS total
FROM budgets AS b
LEFT JOIN budget_items AS bi
    ON bi.budget_id = b.id
WHERE b.department_id = 1
GROUP BY b.id, b.period
ORDER BY b.period_start;

-- 17. Сумма и число бюджетов по подразделениям (страница «Статистика»)
SELECT
    d.name AS department_name,
    COUNT(DISTINCT b.id) AS budgets_count,
    COALESCE(SUM(bi.planned), 0) AS total
FROM departments AS d
LEFT JOIN budgets AS b
    ON b.department_id = d.id
LEFT JOIN budget_items AS bi
    ON bi.budget_id = b.id
GROUP BY d.id, d.name
ORDER BY total DESC;

-- 18. Сумма по статьям расходов во всех бюджетах (страница «Статистика»)
SELECT
    category,
    COUNT(*) AS items_count,
    SUM(planned) AS total
FROM budget_items
GROUP BY category
ORDER BY total DESC;


-- ---------- Фильтрация групп (HAVING) ----------

-- 19. Бюджеты с итогом не менее 600 000 (страница «Статистика»)
SELECT
    b.id,
    b.period,
    d.name AS department_name,
    SUM(bi.planned) AS total
FROM budgets AS b
JOIN departments AS d
    ON b.department_id = d.id
JOIN budget_items AS bi
    ON bi.budget_id = b.id
GROUP BY b.id, b.period, d.name
HAVING SUM(bi.planned) >= 600000
ORDER BY total DESC;

-- 20. Подразделения, у которых больше одного бюджета (страница «Статистика»)
SELECT
    d.name AS department_name,
    COUNT(b.id) AS budgets_count
FROM departments AS d
JOIN budgets AS b
    ON b.department_id = d.id
GROUP BY d.id, d.name
HAVING COUNT(b.id) > 1
ORDER BY budgets_count DESC;
