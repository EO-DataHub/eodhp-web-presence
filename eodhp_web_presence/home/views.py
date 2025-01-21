from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from eodhp_web_presence import settings


def catalogue_page_view(request):
    resource_catalogue_version = settings.RESOURCE_CATALOGUE["version"]
    resource_catalogue_base_url = settings.RESOURCE_CATALOGUE["url"]
    resource_catalogue_url = f"{resource_catalogue_base_url}/{resource_catalogue_version}"
    context = {"url": resource_catalogue_url, "catalogue_data_url": settings.CATALOGUE_DATA["url"]}

    return render(request, "home/catalogue_page.html", context=context)


def workspaces_page_view(request):
    workspaces_version = settings.WORKSPACE_UI["version"]
    workspaces_base_url = settings.WORKSPACE_UI["url"]
    workspaces_url = f"{workspaces_base_url}/{workspaces_version}"
    context = {"url": workspaces_url}

    return render(request, "home/workspaces_page.html", context=context)
