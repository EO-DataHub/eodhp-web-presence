from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import SupportTopicPage

from eodhp_web_presence import settings


def catalogue_page_view(request):
    resource_catalogue_version = settings.RESOURCE_CATALOGUE["version"]
    resource_catalogue_base_url = settings.RESOURCE_CATALOGUE["url"]
    resource_catalogue_url = f"{resource_catalogue_base_url}/{resource_catalogue_version}"
    context = {"url": resource_catalogue_url, "catalogue_data_url": settings.CATALOGUE_DATA["url"]}

    return render(request, "home/catalogue_page.html", context=context)


def search_topics(request):
    query = request.GET.get("query", "")

    if query:
        search_results = SupportTopicPage.objects.live().autocomplete(query)
    else:
        search_results = SupportTopicPage.objects.live().all()

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)


def search_topics_blank(request):
    query = request.GET.get("query", "")

    if query:
        search_results = SupportTopicPage.objects.live().autocomplete(query)
    else:
        search_results = None

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)
