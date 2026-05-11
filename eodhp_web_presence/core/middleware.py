from collections.abc import Callable

import environ
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from home.models import NotificationBanner

env = environ.Env()
IS_PROD = env("IS_PROD", default=False, cast=bool)


class HeaderMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response["Vary"] = "Cookie"
        if not IS_PROD:
            response["X-Robots-Tag"] = "noindex"
        return response


class BannerCacheMiddleware:
    """Prevent wagtailcache from caching page responses when a banner
    schedule boundary (starts_at or ends_at) is closer than the cache
    timeout.  This stops stale banners from starting late or lingering
    after they should have expired.
    """

    _RESTRICTIVE_DIRECTIVES = frozenset({"private", "no-store", "no-cache"})

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def _has_restrictive_cache_control(self, response: HttpResponse) -> bool:
        header = response.get("Cache-Control", "")
        if not header:
            return False
        directives = {directive.strip().lower() for directive in header.split(",")}
        return not directives.isdisjoint(self._RESTRICTIVE_DIRECTIVES)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        cache_timeout = settings.CACHES["default"].get("TIMEOUT", 300)
        if cache_timeout == 0:
            return response

        next_boundary = NotificationBanner.get_next_boundary()
        if next_boundary is None:
            return response

        if self._has_restrictive_cache_control(response):
            return response

        if cache_timeout is None:
            response["Cache-Control"] = "no-cache"
            return response

        time_to_boundary = (next_boundary - timezone.now()).total_seconds()
        if time_to_boundary < cache_timeout:
            response["Cache-Control"] = "no-cache"

        return response
