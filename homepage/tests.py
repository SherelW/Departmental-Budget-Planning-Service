from django.test import SimpleTestCase


class PagesTests(SimpleTestCase):
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

    def test_budget_page_shows_data(self):
        response = self.client.get("/budgets/1/")
        self.assertContains(response, "Зарплата")
