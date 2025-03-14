from django.shortcuts import render

from eodhp_web_presence import settings


def catalogue_page_view(request):
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


def workspaces_page_view(request):
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


def accounts_page_view(request):
    current_username = request.user.username
    return render(
        request=request,
        template_name="home/accounts_page.html",
        context={
            "username": current_username,
        },
    )
