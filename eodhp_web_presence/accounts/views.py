import logging
import secrets
from urllib.parse import quote, urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

# Keycloak required actions that can be triggered for the signed-in user via
# the kc_action parameter on the OIDC authorisation endpoint.
KEYCLOAK_ACTIONS = {
    "update_email": "UPDATE_EMAIL",
    "update_profile": "UPDATE_PROFILE",
}
KEYCLOAK_ACTION_STATE_SESSION_KEY = "keycloak_action_state"


@never_cache
def sign_in(request: HttpRequest) -> HttpResponseRedirect:
    # Honour a validated ?next= target (e.g. from login_required) so the user
    # can complete the action they were attempting after reauthenticating.
    target = None
    for candidate in (request.GET.get("next"), request.headers.get("Referer")):
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            target = candidate
            break

    redirect_tag = f"?rd={quote(target)}" if target else ""

    return redirect(f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNIN']}{redirect_tag}")


@never_cache
def sign_out(request: HttpRequest) -> HttpResponseRedirect:
    keycloak_logout_url = (
        f"{settings.KEYCLOAK['LOGOUT_URL']}"
        f"?client_id={settings.KEYCLOAK['CLIENT_ID']}"
        f"&post_logout_redirect_uri={quote(settings.KEYCLOAK['LOGOUT_REDIRECT_URL'])}"
    )

    oauth2_proxy_logout_url = f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNOUT']}?rd={quote(keycloak_logout_url)}"

    return redirect(oauth2_proxy_logout_url)


@require_GET
@never_cache
@login_required(login_url=reverse_lazy("sign_in"))
def keycloak_action(request: HttpRequest, action: str) -> HttpResponseRedirect:
    """Redirect the user to Keycloak to complete a required action.

    Keycloak renders its own form for the action (e.g. 'Update email') and,
    once completed, returns the user to the accounts page.
    """
    kc_action = KEYCLOAK_ACTIONS.get(action)
    if kc_action is None:
        logger.warning("Unknown Keycloak action requested: %s", action)
        return redirect("/accounts/")

    redirect_uri = settings.KEYCLOAK["KC_ACTION_REDIRECT_URL"] or request.build_absolute_uri(
        reverse("keycloak_action_callback")
    )

    state = secrets.token_urlsafe(32)
    request.session[KEYCLOAK_ACTION_STATE_SESSION_KEY] = state

    params = urlencode(
        {
            "response_type": "code",
            "scope": "openid",
            "client_id": settings.KEYCLOAK["CLIENT_ID"],
            "redirect_uri": redirect_uri,
            "kc_action": kc_action,
            "state": state,
        }
    )

    keycloak_action_url = f"{settings.KEYCLOAK['AUTH_URL']}?{params}"
    logger.debug("Redirecting user '%s' to Keycloak action '%s'", request.user.username, kc_action)

    return redirect(keycloak_action_url)


@require_GET
@never_cache
def keycloak_action_callback(request: HttpRequest) -> HttpResponseRedirect:
    """Return URL for Keycloak required-action flows.

    The authorisation response cannot be consumed here - oauth2-proxy owns the
    OIDC session. Restarting the proxy session (sign out of the proxy, then
    straight back in) forces it to obtain a fresh token containing the updated
    claims. The Keycloak SSO session keeps this transparent to the user.
    """
    expected_state = request.session.pop(KEYCLOAK_ACTION_STATE_SESSION_KEY, None)
    returned_state = request.GET.get("state")
    code = request.GET.get("code")
    if (
        not expected_state
        or not returned_state
        or not secrets.compare_digest(expected_state, returned_state)
        or not code
    ):
        logger.warning("Invalid or incomplete Keycloak action callback")
        return redirect("/accounts/")

    accounts_url = request.build_absolute_uri("/accounts/")
    sign_in_url = f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNIN']}?rd={quote(accounts_url)}"

    return redirect(f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNOUT']}?rd={quote(sign_in_url)}")
