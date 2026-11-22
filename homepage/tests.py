from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from budgets.models import Budget, BudgetItem
from departments.models import Department


class DataMixin:
    """Тестовые данные: 3 подразделения, 4 бюджета, 9 статей."""

    @staticmethod
    def make_budget(department, period, start, end, items):
        budget = Budget.objects.create(
            department=department,
            period=period,
            period_start=start,
            period_end=end,
        )
        for category, planned in items:
            BudgetItem.objects.create(
                budget=budget,
                category=category,
                planned=Decimal(planned),
            )
        return budget

    @classmethod
    def setUpTestData(cls):
        cls.finance = Department.objects.create(
            name="Подразделение финансов", head="Иванов И."
        )
        cls.it = Department.objects.create(
            name="IT-отдел", head="Петров П."
        )
        cls.marketing = Department.objects.create(
            name="Отдел маркетинга", head="Сидорова А."
        )
        sept = (date(2026, 9, 1), date(2026, 9, 30))
        octo = (date(2026, 10, 1), date(2026, 10, 31))

        cls.fin_sept = cls.make_budget(
            cls.finance, "01.09.2026 - 30.09.2026", *sept,
            [("Зарплата", "500000"), ("Командировки", "50000"),
             ("Канцтовары", "20000")],
        )
        cls.it_sept = cls.make_budget(
            cls.it, "01.09.2026 - 30.09.2026", *sept,
            [("Зарплата", "700000"), ("Оборудование", "300000")],
        )
        cls.fin_oct = cls.make_budget(
            cls.finance, "01.10.2026 - 31.10.2026", *octo,
            [("Зарплата", "500000"), ("Командировки", "30000")],
        )
        cls.mkt_sept = cls.make_budget(
            cls.marketing, "01.09.2026 - 30.09.2026", *sept,
            [("Реклама", "250000"), ("Зарплата", "300000")],
        )


class ModelTests(DataMixin, TestCase):
    def test_str(self):
        self.assertEqual(str(self.it), "IT-отдел")
        self.assertIn("IT-отдел", str(self.it_sept))

    def test_reverse_relations(self):
        self.assertEqual(self.finance.budgets.count(), 2)
        self.assertEqual(self.fin_sept.items.count(), 3)

    def test_total_planned(self):
        self.assertEqual(self.fin_sept.get_total_planned(), 570000)
        empty = Budget.objects.create(
            department=self.it,
            period="01.11.2026 - 30.11.2026",
            period_start=date(2026, 11, 1),
            period_end=date(2026, 11, 30),
        )
        self.assertEqual(empty.get_total_planned(), 0)

    def test_department_with_budgets_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.finance.delete()

    def test_deleting_budget_deletes_items(self):
        pk = self.fin_sept.pk
        self.fin_sept.delete()
        self.assertFalse(BudgetItem.objects.filter(budget_id=pk).exists())

    def test_planned_must_be_positive(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                BudgetItem.objects.create(
                    budget=self.fin_sept,
                    category="Плохая статья",
                    planned=Decimal("-5"),
                )

    def test_period_start_must_not_be_after_end(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Budget.objects.create(
                    department=self.it,
                    period="плохой период",
                    period_start=date(2026, 12, 1),
                    period_end=date(2026, 11, 1),
                )


class PagesTests(DataMixin, TestCase):
    def test_existing_pages_return_200(self):
        urls = [
            "/", "/departments/", f"/departments/{self.finance.pk}/",
            "/budgets/", f"/budgets/{self.fin_sept.pk}/",
            "/budgets/search/", "/budgets/statistics/",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_objects_return_404(self):
        for url in [
            "/departments/999999/", "/budgets/999999/", "/nonexistent/",
            "/budgets/abc/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_templates_used(self):
        cases = {
            "/": "homepage/index.html",
            "/departments/": "departments/department_list.html",
            f"/departments/{self.it.pk}/":
                "departments/department_detail.html",
            "/budgets/": "budgets/budget_list.html",
            f"/budgets/{self.it_sept.pk}/": "budgets/budget_detail.html",
            "/budgets/search/": "budgets/budget_search.html",
            "/budgets/statistics/": "budgets/statistics.html",
        }
        for url, template in cases.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertTemplateUsed(response, "base.html")

    def test_budget_detail_shows_related_data_and_total(self):
        response = self.client.get(f"/budgets/{self.fin_sept.pk}/")
        budget = response.context["budget"]
        self.assertEqual(budget.total, Decimal("570000"))
        self.assertEqual(budget.department.name, self.finance.name)
        self.assertEqual(len(response.context["items"]), 3)
        self.assertContains(response, "Зарплата")

    def test_department_detail_total(self):
        response = self.client.get(f"/departments/{self.finance.pk}/")
        self.assertEqual(response.context["total"], Decimal("1100000"))
        self.assertEqual(len(response.context["budgets"]), 2)
        self.assertEqual(len(response.context["items"]), 5)


class DepartmentSearchTests(DataMixin, TestCase):
    def count(self, query):
        response = self.client.get("/departments/", {"q": query})
        return len(response.context["departments"])

    def test_search_without_query_returns_all(self):
        self.assertEqual(self.count(""), 3)

    def test_search_by_name(self):
        self.assertEqual(self.count("IT"), 1)

    def test_search_by_head(self):
        self.assertEqual(self.count("Петров"), 1)

    def test_search_without_results(self):
        response = self.client.get("/departments/", {"q": "zzz"})
        self.assertContains(response, "Подразделения не найдены.")


class BudgetListTests(DataMixin, TestCase):
    def get(self, **params):
        return self.client.get("/budgets/", params)

    def test_pagination(self):
        page = self.get().context["page_obj"]
        self.assertEqual(page.paginator.count, 4)
        self.assertEqual(page.paginator.num_pages, 2)
        self.assertEqual(len(page), 3)
        self.assertEqual(len(self.get(page=2).context["page_obj"]), 1)

    def test_invalid_page_number_opens_first_page(self):
        self.assertEqual(self.get(page="abc").context["page_obj"].number, 1)

    def test_page_out_of_range_opens_last_page(self):
        self.assertEqual(self.get(page=99).context["page_obj"].number, 2)

    def test_filter_by_department(self):
        page = self.get(department=self.it.pk).context["page_obj"]
        self.assertEqual(page.paginator.count, 1)

    def test_filter_by_date(self):
        page = self.get(date="2026-10-15").context["page_obj"]
        self.assertEqual(page.paginator.count, 1)

    def test_filter_by_date_and_department(self):
        page = self.get(
            date="2026-09-15", department=self.finance.pk
        ).context["page_obj"]
        self.assertEqual(page.paginator.count, 1)

    def test_search_by_related_name(self):
        page = self.get(q="IT").context["page_obj"]
        self.assertEqual(page.paginator.count, 1)

    def test_invalid_date_shows_error(self):
        response = self.get(date="abc")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Укажите корректную дату.")

    def test_invalid_department_is_ignored(self):
        for value in ["abc", "-1", "9" * 30]:
            with self.subTest(value=value):
                response = self.get(department=value)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.context["page_obj"].paginator.count, 4
                )

    def test_sort_by_total(self):
        rows = list(self.get(sort="total").context["page_obj"])
        self.assertEqual(rows[0]["department_name"], "IT-отдел")

    def test_sort_by_department(self):
        rows = list(self.get(sort="department").context["page_obj"])
        self.assertEqual(rows[0]["department_name"], "IT-отдел")

    def test_unknown_sort_falls_back_to_period(self):
        response = self.get(sort="id; DROP TABLE")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["sort"], "period")

    def test_pagination_links_keep_filters(self):
        response = self.get(sort="total")
        self.assertContains(response, "sort=total")
        self.assertContains(response, "page=2")


class SearchAndStatisticsTests(DataMixin, TestCase):
    def test_search_without_date_shows_only_form(self):
        response = self.client.get("/budgets/search/")
        self.assertFalse(response.context["searched"])

    def test_search_by_date(self):
        response = self.client.get(
            "/budgets/search/", {"date": "2026-10-15"}
        )
        self.assertEqual(len(response.context["budgets"]), 1)
        self.assertEqual(len(response.context["free_departments"]), 2)

    def test_search_on_period_boundary(self):
        response = self.client.get(
            "/budgets/search/", {"date": "2026-09-30"}
        )
        self.assertEqual(len(response.context["budgets"]), 3)

    def test_search_date_without_budgets(self):
        response = self.client.get(
            "/budgets/search/", {"date": "2030-01-01"}
        )
        self.assertEqual(len(response.context["budgets"]), 0)
        self.assertEqual(len(response.context["free_departments"]), 3)
        self.assertContains(response, "действующих бюджетов нет")

    def test_search_invalid_date(self):
        response = self.client.get("/budgets/search/", {"date": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Некорректная дата")

    def test_statistics_values(self):
        context = self.client.get("/budgets/statistics/").context
        self.assertEqual(context["budgets_count"], 4)
        self.assertEqual(context["totals"]["total_planned"], 2650000)
        self.assertEqual(context["totals"]["max_item"], 700000)
        top = list(context["top_items"])
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0]["planned"], 700000)

    def test_statistics_includes_department_without_budgets(self):
        Department.objects.create(name="Пустой отдел", head="Нет Н.")
        context = self.client.get("/budgets/statistics/").context
        rows = {
            row["department_name"]: row for row in context["by_department"]
        }
        self.assertEqual(rows["Пустой отдел"]["budgets_count"], 0)
        self.assertEqual(rows["Пустой отдел"]["total"], 0)
        self.assertEqual(rows["Подразделение финансов"]["budgets_count"], 2)

    def test_statistics_having_parameter(self):
        url = "/budgets/statistics/"
        low = self.client.get(url, {"min_total": "500000"}).context
        self.assertEqual(len(low["large_budgets"]), 4)
        high = self.client.get(url, {"min_total": "5000000"}).context
        self.assertEqual(len(high["large_budgets"]), 0)

    def test_statistics_invalid_parameter(self):
        for value in ["abc", "-5", "nan", "1e30"]:
            with self.subTest(value=value):
                response = self.client.get(
                    "/budgets/statistics/", {"min_total": value}
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "неотрицательным числом")

    def test_departments_with_several_budgets(self):
        context = self.client.get("/budgets/statistics/").context
        rows = list(context["busy_departments"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["budgets_count"], 2)


class LayoutTests(DataMixin, TestCase):
    def test_navigation_links(self):
        response = self.client.get("/")
        for url in ["/departments/", "/budgets/", "/budgets/statistics/"]:
            self.assertContains(response, f'href="{url}"')

    def test_static_files_linked(self):
        response = self.client.get("/")
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/img/logo.png")
