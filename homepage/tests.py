from django.test import TestCase


class PagesTests(TestCase):
    def test_existing_pages_return_200(self):
        for url in [
            "/", "/departments/", "/departments/1/",
            "/budgets/", "/budgets/1/",
            "/budgets/search/", "/budgets/statistics/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_objects_return_404(self):
        for url in [
            "/departments/999/", "/budgets/999/", "/nonexistent/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_non_numeric_id_is_404(self):
        self.assertEqual(self.client.get("/budgets/abc/").status_code, 404)

    def test_templates_used(self):
        cases = {
            "/": "homepage/index.html",
            "/departments/": "departments/department_list.html",
            "/departments/1/": "departments/department_detail.html",
            "/budgets/": "budgets/budget_list.html",
            "/budgets/1/": "budgets/budget_detail.html",
            "/budgets/search/": "budgets/budget_search.html",
            "/budgets/statistics/": "budgets/statistics.html",
        }
        for url, template in cases.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertTemplateUsed(response, "base.html")

    def test_budget_page_shows_data_from_sqlite(self):
        response = self.client.get("/budgets/1/")
        self.assertEqual(response.context["budget"]["id"], 1)
        self.assertContains(response, "Зарплата")
        self.assertContains(response, "570")

    def test_missing_budget_shows_message(self):
        response = self.client.get("/budgets/999/")
        self.assertContains(response, "Бюджет не найден", status_code=404)

    def test_budget_list_has_all_budgets(self):
        response = self.client.get("/budgets/")
        self.assertEqual(len(response.context["budgets"]), 4)

    def test_search_without_date_shows_only_form(self):
        response = self.client.get("/budgets/search/")
        self.assertFalse(response.context["searched"])

    def test_search_by_date(self):
        response = self.client.get("/budgets/search/?date=2026-10-15")
        self.assertEqual(len(response.context["budgets"]), 1)
        self.assertEqual(len(response.context["free_departments"]), 2)

    def test_search_with_date_without_budgets(self):
        response = self.client.get("/budgets/search/?date=2030-01-01")
        self.assertEqual(response.context["budgets"], [])
        self.assertContains(response, "действующих бюджетов нет")

    def test_search_with_invalid_date(self):
        response = self.client.get("/budgets/search/?date=abc")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Некорректная дата")

    def test_statistics_having_parameter(self):
        response = self.client.get("/budgets/statistics/?min_total=500000")
        self.assertEqual(len(response.context["large_budgets"]), 4)
        response = self.client.get("/budgets/statistics/?min_total=5000000")
        self.assertEqual(len(response.context["large_budgets"]), 0)

    def test_statistics_invalid_parameter(self):
        response = self.client.get("/budgets/statistics/?min_total=abc")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "неотрицательным числом")

    def test_navigation_links(self):
        response = self.client.get("/")
        for url in ["/departments/", "/budgets/", "/budgets/statistics/"]:
            self.assertContains(response, f'href="{url}"')

    def test_static_files_linked(self):
        response = self.client.get("/")
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/img/logo.png")
