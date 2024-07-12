from collections.abc import Callable
from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse


@dataclass(frozen=True)
class AuthRequest:
    user_roles: list[str]
    path: str


class AuthMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if is_authenticated := "Authorization" in request.headers:
            roles: list[str] = extract_roles(request.headers["Authorization"])
        else:
            roles = []

        if is_allowed(AuthRequest(roles, request.path)):
            response = self.get_response(request)
        elif not is_authenticated:
            return HttpResponse("Unauthorized", status=401)
        else:
            return HttpResponse("Forbidden", status=403)

        return response


def extract_roles(auth_header: str) -> list[str]:
    # extract roles from the auth header
    return []  # default for initial testing


def is_allowed(request: AuthRequest) -> bool:
    # call opa to determine if the request is allowed
    return True  # default for initial testing
