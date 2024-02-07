import os
import pytest


@pytest.fixture(autouse=True)
def environment_variables():
    os.environ["DJANGO_SETTINGS_MODULE"] = "eodhp_web_presence"
