import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

import requests
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse

from . import tokens
from .models import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuthRequest:
    user_roles: list[str]
    path: str

    def to_dict(self) -> dict[str, any]:
        return {
            "input": {
                "path": self.path,
                "roles": self.user_roles,
            },
        }


class AuthMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
        opa_server_url: Optional[str] = None,
    ):
        self.get_response = get_response
        self.opa_server_url = opa_server_url

    def __call__(self, request: HttpRequest) -> HttpResponse:
        claims: tokens.UserClaims = tokens.extract_claims(
            request.headers.get("Authorization", None),
        )

        logger.debug("User claims: %s", json.dumps(claims.to_dict(), indent=2))

        user: User | None = authenticate(request, username=claims.username)

        if user is not None:
            logger.debug("User authenticated as %s", user.username)
            login(request, user)
        else:
            logger.debug("User not authenticated")

        if self.is_allowed(AuthRequest(claims.roles, request.path)):
            logger.debug("User is authorized to access path")
            response = self.get_response(request)
        elif user is None:
            logger.debug("User is not authorized to access path and should authenticate")
            return HttpResponse("Unauthorized", status=401)
        else:
            logger.debug("User is authenticated but is not authorized to view path")
            return HttpResponse("Forbidden", status=403)

        return response

    def is_allowed(self, request: AuthRequest) -> bool:
        if self.opa_server_url is None:
            return True  # always allow if no OPA server is configured

        response = requests.post(
            self.opa_server_url,
            headers={"Content-Type": "application/json"},
            json=request.to_dict(),
        )

        if not response.ok:
            logger.error(
                "OPA server '%s' returned an error: %s",
                self.opa_server_url,
                response.content.decode(),
            )
            return False

        return json.loads(response.content.decode())["result"]
