from collections.abc import Callable

import environ
from django.http import HttpRequest, HttpResponse

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
