import logging

import requests
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def sign_in(request):
    return redirect("/oauth2/start")


def sign_out(request):
    r1 = requests.post(
        settings["KEYCLOAK"]["LOGOUT_URL"], data={"client_id": settings["KEYCLOAK"]["CLIENT_ID"]}
    )
    if not r1.ok:
        logger.error("Failed to logout from Keycloak: %s", r1.text)
        return

    r2 = requests.get("/oauth2/sign_out")
    if not r2.ok:
        logger.error("Failed to logout from Oauth2 Proxy: %s", r2.text)
        return

    logout(request)
    return redirect("/oauth2/sign_out")
