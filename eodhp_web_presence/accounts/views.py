import logging
from urllib.parse import parse_qs, quote

from django.conf import settings
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


def sign_in(request):
    referer = request.META["HTTP_REFERER"]
    logger.debug("REFERRER HEADER: %s", referer)
    # query = referer.split("?")[1]
    query = referer.partition("?")[2]
    logger.debug("QUERY STRING: %s", query)
    q = parse_qs(query)
    # logger.debug("QUERY STRING: %s", query)
    logger.debug("QUERY: %s", q)
    return redirect(settings.KEYCLOAK["OAUTH2_PROXY_SIGNIN"])


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
