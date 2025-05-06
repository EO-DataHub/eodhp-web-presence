import json
import logging
from collections.abc import Callable

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse

from . import tokens
from .models import User

logger = logging.getLogger(__name__)


class ClaimsMiddleware:
    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse], *, force_logout: bool = True
    ):
        self.get_response = get_response
        self.force_logout = force_logout

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
        request.user.email = claims.email

        if (
            self.force_logout
            and request.user.is_authenticated
            and claims.username != request.user.username
        ):
            username = request.user.username
            logger.debug(
                "User (%s) is authenticated but the claims username (%s) does not match",
                username,
                claims.username,
            )
            auth.logout(request)
            logger.debug("User '%s' logged out", username)

        if not request.user.is_authenticated and claims.username is not None:
            user: User | None = auth.authenticate(request)

            if user is not None:
                logger.debug("User authenticated as %s", user.username)
                auth.login(request, user)
            else:
                logger.debug("User not authenticated")

        return self.get_response(request)
