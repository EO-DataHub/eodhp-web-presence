from django.test import TestCase
from eodhp_web_presence import home  #noqa: F401


class TestHome(TestCase):
    def test_status_code__success(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
