import os

from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eodhp_web_presence.settings")

import django

django.setup()


class TestHome(TestCase):
    def test_status_code__success(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
