from django.test import TestCase


class TestHome(TestCase):
    def test_status_code__success(self):
        home_page_get = self.client.get("/")
        assert home_page_get.status_code == 200
        assert b"Home" in home_page_get.content
