from django.test import TestCase


class PagesTests(TestCase):
    def test_existing_pages_return_200(self):
        for url in [
            "/", "/departments/", "/departments/1/",
            "/budgets/", "/budgets/1/",
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
        }
        for url, template in cases.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertTemplateUsed(response, "base.html")
                self.assertTemplateUsed(response, "includes/navigation.html")

    def test_include_used_in_lists(self):
        response = self.client.get("/departments/")
        self.assertTemplateUsed(
            response, "departments/includes/department_card.html"
        )
        response = self.client.get("/budgets/")
        self.assertTemplateUsed(
            response, "budgets/includes/budget_status.html"
        )

    def test_context_passed_to_template(self):
        response = self.client.get("/budgets/1/")
        self.assertEqual(response.context["budget"].id, 1)
        self.assertContains(response, "Зарплата")

    def test_missing_budget_shows_message(self):
        response = self.client.get("/budgets/999/")
        self.assertContains(response, "Бюджет не найден", status_code=404)

    def test_navigation_links_use_named_urls(self):
        response = self.client.get("/")
        self.assertContains(response, 'href="/departments/"')
        self.assertContains(response, 'href="/budgets/"')

    def test_static_files_linked(self):
        response = self.client.get("/")
        self.assertContains(response, "/static/homepage/css/style.css")
        self.assertContains(response, "/static/homepage/js/main.js")
        self.assertContains(response, "/static/homepage/img/logo.png")
