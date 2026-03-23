import django.conf


def pytest_configure() -> None:
    django.conf.settings.STORAGES = {
        **django.conf.settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
