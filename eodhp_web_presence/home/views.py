from django.shortcuts import render

from eodhp_web_presence import settings


def catalogue_page_view(request):
    return render(
        request,
        "home/catalogue_page.html",
        {
            "url": f"{settings.RESOURCE_CATALOGUE['url']}/{settings.RESOURCE_CATALOGUE['version']}",
            "catalogue_data_url": settings.CATALOGUE_DATA["url"],
        },
    )


def workspaces_page_view(request):
    return render(
        request,
        "home/workspaces_page.html",
        {"url": f"{settings.WORKSPACE_UI['url']}/{settings.WORKSPACE_UI['version']}"},
    )


def accounts_page_view(request):
    return render(request, "home/accounts_page.html")
