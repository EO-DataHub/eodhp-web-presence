from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from eodhp_web_presence import settings


def catalogue_page_view(request: HttpRequest) -> HttpResponse:
    return render(
        request=request,
        template_name="home/catalogue_page.html",
        context={
            "url": "{url}/{version}".format(
                url=settings.RESOURCE_CATALOGUE["url"],
                version=settings.RESOURCE_CATALOGUE["version"],
            ),
            "catalogue_data_url": settings.CATALOGUE_DATA["url"],
        },
    )


def workspaces_page_view(request: HttpRequest) -> HttpResponse:
    return render(
        request=request,
        template_name="home/workspaces_page.html",
        context={
            "url": "{url}/{version}".format(
                url=settings.WORKSPACE_UI["url"],
                version=settings.WORKSPACE_UI["version"],
            ),
        },
    )


def eodhp_guide_page_view(request: HttpRequest) -> HttpResponse:
    return redirect(
        "{url}/{version}/index.html".format(
            url=settings.EODHP_GUIDE["url"],
            version=settings.EODHP_GUIDE["version"],
        )
    )


@never_cache
def accounts_page_view(request: HttpRequest) -> HttpResponse:
    current_username = request.user.username

    # Logged-in user's Keycloak profile, taken from the OIDC claims attached
    # by the claims middleware when available, falling back to the user model.
    claims = getattr(request, "claims", None)
    profile = None
    if request.user.is_authenticated:
        profile = {
            "username": current_username,
            "first_name": (claims.given_name if claims else None) or request.user.first_name or "",
            "last_name": (claims.family_name if claims else None) or request.user.last_name or "",
            "email": (claims.email if claims else None) or request.user.email or "",
        }

    return render(
        request=request,
        template_name="home/accounts_page.html",
        context={
            "username": current_username,
            "profile": profile,
        },
    )
