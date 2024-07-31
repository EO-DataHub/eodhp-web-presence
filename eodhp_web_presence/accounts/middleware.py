import json
from collections.abc import Callable
from dataclasses import dataclass

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse

from . import tokens
from .models import User


@dataclass(frozen=True)
class AuthRequest:
    user_roles: list[str]
    path: str


class AuthMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response
        self._opal_server_url = settings.EODHP_AUTH["OPAL_SERVER_URL"]

    def __call__(self, request: HttpRequest) -> HttpResponse:
        claims: tokens.UserClaims = tokens.extract_claims(
            request.headers.get("Authorization", None),
        )

        user: User | None = authenticate(request, username=claims.username)

        if user is not None:
            login(request, user)

        if self._is_allowed(AuthRequest(claims.roles, request.path)):
            response = self.get_response(request)
        elif user is None:
            return HttpResponse("Unauthorized", status=401)
        else:
            return HttpResponse("Forbidden", status=403)

        return response

    def _is_allowed(self, request: AuthRequest) -> bool:
        response = requests.post(
            self._opal_server_url,
            headers={"Content-Type": "application/json"},
            json={"input": {"path": request.path, "roles": request.user_roles}},
        )

        return json.loads(response.content.decode())["result"]
