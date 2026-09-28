import logging
from collections.abc import Callable
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse

audit_logger = logging.getLogger("accounts.audit")


def is_hub_admin(request: HttpRequest) -> bool:
    user = request.user
    if not (user.is_authenticated and user.is_active and user.is_superuser):
        return False
    if settings.OIDC_CLAIMS["ENABLED"]:
        # Check the current token so a revoked role takes effect on the next request, not the next login
        claims = getattr(request, "claims", None)
        return bool(claims and claims.admin)
    return True


def hub_admin_required(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    @wraps(view)
    def wrapped(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not settings.KEYCLOAK["USER_LIST_ENABLED"]:
            raise Http404
        if not is_hub_admin(request):
            audit_logger.warning("hub-users access denied user=%s path=%s", request.user, request.path)
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped
