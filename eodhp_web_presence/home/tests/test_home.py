from django.test import TestCase
from wagtail.models import Page


class TestHome(TestCase):
    def test_status_code__success(self):
        with self.assertRaises(Page.DoesNotExist):
            self.client.get("/")
