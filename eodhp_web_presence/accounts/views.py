import logging

import requests
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)


def sign_in(request):
    return redirect(settings.KEYCLOAK["OAUTH2_PROXY_SIGNIN"])


def sign_out(request):
    try:
        r1 = requests.post(
            settings.KEYCLOAK["LOGOUT_URL"], data={"client_id": settings.KEYCLOAK["CLIENT_ID"]}
        )
    except ConnectionError as e:
        logger.error("Failed to connect to Keycloak: %s", e)
    else:
        if not r1.ok:
            logger.error("Failed to logout from Keycloak: %s", r1.text)

    try:
        r2 = requests.get(settings.KEYCLOAK["OAUTH2_PROXY_SIGNOUT"])
    except ConnectionError as e:
        logger.error("Failed to connect to Oauth2 Proxy: %s", e)
    else:
        if not r2.ok:
            logger.error("Failed to logout from Oauth2 Proxy: %s", r2.text)

    logout(request)
    return redirect("/")
