from django.test import TestCase

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eodhp_web_presence.settings'


class TestHome(TestCase):
    def test_status_code__success(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
