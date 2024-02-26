import os
from unittest import mock

import pytest
from django.test import TestCase
from importlib import reload

from eodhp_web_presence import settings


@pytest.fixture(autouse=True)
def environment_variables():
    with mock.patch.dict(
        os.environ, {"STAC_BROWSER_URL": "http://this-is-a-test-stac-browser-url.com"}
    ):
        yield



class TestHome(TestCase):
    def test_status_code__success(self):
        reload(settings)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
