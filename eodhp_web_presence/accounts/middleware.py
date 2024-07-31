import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
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


class ClaimsMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "The claims middleware requires the authentication middleware"
                "to be installed. Edit your MIDDLEWARE setting to insert"
                "'django.contrib.auth.middleware.AuthenticationMiddleware' "
                "before the ClaimsMiddleware class."
            )

        claims = tokens.extract_claims(
            request.headers.get("Authorization", None),
        )
        logger.debug("User claims: %s", json.dumps(claims.to_dict(), indent=2))
        request.claims = claims

        if isinstance(request.user, AnonymousUser) and claims.username is not None:
            user: User | None = authenticate(request)

            if user is not None:
                logger.debug("User authenticated as %s", user.username)
                login(request, user)
            else:
                logger.debug("User not authenticated")

        return self.get_response(request)


class OPAAuthorizationMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
        opa_server_url: Optional[str],
    ):
        self.get_response = get_response
        self.opa_server_url = opa_server_url

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not hasattr(request, "claims"):
            raise ImproperlyConfigured(
                "The OPA authorization middleware requires the claims middleware"
                "to be installed. Edit your MIDDLEWARE setting to insert"
                "'accounts.middleware.ClaimsMiddleware' before the ClaimsMiddleware "
                "class."
            )

        if self.is_allowed(AuthRequest(request.claims.roles, request.path)):
            logger.debug("User is authorized to access path")
            response = self.get_response(request)
        elif isinstance(request.user, AnonymousUser):
            logger.debug("User is not authorized to access path and should authenticate")
            return HttpResponse("Unauthorized", status=401)
        else:
            logger.debug("User is authenticated but is not authorized to view path")
            return HttpResponse("Forbidden", status=403)

        return response

    def is_allowed(self, request: AuthRequest) -> bool:
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
