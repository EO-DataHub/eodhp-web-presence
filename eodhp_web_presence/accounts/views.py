import logging
from urllib.parse import quote

from django.conf import settings
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def sign_in(request):
    referer = request.headers.get("Referer")

    redirect_tag = f"?rd={quote(referer)}" if referer else ""

    return redirect(f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNIN']}{redirect_tag}")


def sign_out(request):
    keycloak_logout_url = (
        f"{settings.KEYCLOAK['LOGOUT_URL']}"
        f"?client_id={settings.KEYCLOAK['CLIENT_ID']}"
        f"&post_logout_redirect_uri={quote(settings.KEYCLOAK['LOGOUT_REDIRECT_URL'])}"
    )

    oauth2_proxy_logout_url = (
        f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNOUT']}?rd={quote(keycloak_logout_url)}"
    )

    return redirect(oauth2_proxy_logout_url)
