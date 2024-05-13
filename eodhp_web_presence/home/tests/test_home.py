from django.test import TestCase


class TestHome(TestCase):
    def test_status_code__success(self):
        response = self.client.get("/index")
        self.assertEqual(response.status_code, 200)
