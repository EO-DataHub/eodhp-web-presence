"""
Django settings for eodhp_web_presence project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import importlib
import logging
import os

import environ
from storages.backends.s3boto3 import S3Boto3Storage

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


env = environ.Env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=bool, default=False)


# Application definition

INSTALLED_APPS = [
    # django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # 3rd party
    "modelcluster",
    "taggit",
    "django_sass",
    "wagtailcache",
    # web presence
    "accounts",
    "core",
    "home",
]

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.ClaimsBackend",
    "django.contrib.auth.backends.ModelBackend",  # Keep the default backend for admin access
]

KEYCLOAK = {
    "CLIENT_ID": env("KEYCLOAK_CLIENT_ID", default="oauth2-proxy"),
    "LOGOUT_URL": env(
        "KEYCLOAK_LOGOUT_URL",
        default="http://127.0.0.1/keycloak/realms/master/protocol/openid-connect/logout",
    ),
    "LOGOUT_REDIRECT_URL": env("KEYCLOAK_LOGOUT_REDIRECT_URL", default="http://127.0.0.1"),
    "OAUTH2_PROXY_SIGNIN": env("OAUTH2_PROXY_SIGNIN", default="http://127.0.0.1/oauth2/start"),
    "OAUTH2_PROXY_SIGNOUT": env("OAUTH2_PROXY_SIGNOUT", default="http://127.0.0.1/oauth2/sign_out"),
}
OIDC_CLAIMS = {
    "ENABLED": env("OIDC_CLAIMS_ENABLED", cast=bool, default=False),
    "USERNAME_PATH": env("OIDC_CLAIMS_USERNAME_PATH", cast=str, default=None),
    "ROLES_PATH": env("OIDC_CLAIMS_ROLES_PATH", cast=str, default=None),
    "SUPERUSER_ROLE": env("OIDC_CLAIMS_SUPERUSER_ROLE", cast=str, default=None),
    "MODERATOR_ROLE": env("OIDC_CLAIMS_MODERATOR_ROLE", cast=str, default=None),
    "EDITOR_ROLE": env("OIDC_CLAIMS_EDITOR_ROLE", cast=str, default=None),
}


def claims_middleware_factory(get_response):
    module_name = "accounts.middleware"
    class_name = "ClaimsMiddleware"

    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)

    return cls(get_response, force_logout=True)


MIDDLEWARE = [
    # UpdateCacheMiddleware to be at top
    "wagtailcache.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise Middleware above all but below Security
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "core.middleware.HeaderMiddleware",
    "wagtailcache.cache.FetchFromCacheMiddleware",  # must be last
]

if OIDC_CLAIMS["ENABLED"]:
    MIDDLEWARE.insert(7, "eodhp_web_presence.settings.claims_middleware_factory")

WHITENOISE_MAX_AGE = env("STATIC_FILE_CACHE_LENGTH", cast=int, default=3600)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache"),
        "KEY_PREFIX": "wagtailcache",
        "TIMEOUT": env("PAGE_CACHE_LENGTH", cast=int, default=300),  # seconds
    }
}

ROOT_URLCONF = "eodhp_web_presence.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.menu_links",
            ],
        },
    },
]

WSGI_APPLICATION = "eodhp_web_presence.wsgi.application"

EOX_VIEWSERVER = {"url": env("EOX_VIEWSERVER_URL", default=None)}
NOTEBOOKS = {"url": env("NOTEBOOKS_URL", default=None)}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env("SQL_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("SQL_DATABASE", default=os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": env("SQL_USER", default="user"),
        "PASSWORD": env("SQL_PASSWORD", default="password"),
        "HOST": env("SQL_HOST", default="localhost"),
        "PORT": env("SQL_PORT", default="5432"),
    }
}

# Support schema definition for Postgres
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"]["OPTIONS"] = {
        "options": f"-c search_path={env('SQL_SCHEMA', default='public')}",
    }

RESOURCE_CATALOGUE = {
    "version": env("RESOURCE_CATALOGUE_VERSION", default="v1.0.0"),
    "url": env("RESOURCE_CATALOGUE_URL", default=None),
}

WORKSPACE_UI = {
    "version": env("WORKSPACE_UI_VERSION", default="v1.0.0"),
    "url": env("WORKSPACE_UI_URL", default=None),
}

CATALOGUE_DATA = {"url": env("CATALOGUE_DATA_URL", default=None)}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


if env("USE_S3", default=False, cast=bool):
    # Set the required AWS credentials
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="static-web-artefacts-eodhp")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="eu-west-2")

    # Set the media files locations relative to the S3 bucket
    MEDIAFILES_LOCATION = env("MEDIAFILES_LOCATION", default="static-apps/web-presence-media/media")

    # Configure media files storage
    class MediaStorage(S3Boto3Storage):
        location = MEDIAFILES_LOCATION
        file_overwrite = False

    STORAGES["default"]["BACKEND"] = "eodhp_web_presence.settings.MediaStorage"
    MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{MEDIAFILES_LOCATION}/"
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
    MEDIA_URL = "/media/"


# Wagtail settings

WAGTAIL_SITE_NAME = "eodhp_web_presence"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = env("BASE_URL", default="www.example.com")


# SECRET KEY (Used for cryptographic signing)
SECRET_KEY = env("SECRET_KEY", default="None")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [
    host.strip() for host in env("ALLOWED_HOSTS", default="localhost, 127.0.0.1").split(",")
]

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOG_LEVEL = logging.DEBUG if DEBUG else logging.WARNING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{asctime} {levelname} {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "accounts": {"handlers": ["console"], "level": LOG_LEVEL},
        "core": {"handlers": ["console"], "level": LOG_LEVEL},
        "eodhp_web_presence": {"handlers": ["console"], "level": LOG_LEVEL},
        "home": {"handlers": ["console"], "level": LOG_LEVEL},
    },
}

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
