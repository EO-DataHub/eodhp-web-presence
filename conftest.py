import pytest


@pytest.fixture(autouse=True)
def _use_simple_staticfiles(settings: object) -> None:
    """Use plain StaticFilesStorage in tests so collectstatic is not required."""
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
