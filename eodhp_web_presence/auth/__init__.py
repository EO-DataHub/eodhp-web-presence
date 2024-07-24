import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin

import environ
import jwt
import requests
from django.http import HttpRequest, HttpResponse

env = environ.Env()


@dataclass(frozen=True)
class AuthRequest:
    user_roles: list[str]
    path: str


class AuthMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if env("ENABLE_OPA", cast=bool, default=False):
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

        else:
            response = self.get_response(request)

        return response


def extract_roles(auth_header: str) -> list[str]:
    token = auth_header.split()[1]

    claims = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])

    if "realm_access" in claims:
        return claims.get("realm_access", {}).get("roles", [])
    return []


def is_allowed(request: AuthRequest) -> bool:
    opal_server_url = urljoin(os.environ["OPAL_SERVER"], os.environ["OPAL_PATH"])

    response = requests.post(
        opal_server_url,
        headers={"Content-Type": "application/json"},
        json={"input": {"path": request.path, "roles": request.user_roles}},
    )

    return json.loads(response.content.decode())["result"]
