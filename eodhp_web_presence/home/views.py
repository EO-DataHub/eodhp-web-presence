from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from wagtail.models import Page

from eodhp_web_presence import settings

from .models import SupportTopicPage


def catalogue_page_view(request):
    resource_catalogue_version = settings.RESOURCE_CATALOGUE["version"]
    resource_catalogue_base_url = settings.RESOURCE_CATALOGUE["url"]
    resource_catalogue_url = f"{resource_catalogue_base_url}/{resource_catalogue_version}"
    context = {"url": resource_catalogue_url, "catalogue_data_url": settings.CATALOGUE_DATA["url"]}

    return render(request, "home/catalogue_page.html", context=context)


def search_topics(request):
    query = request.GET.get("query", "")
    area_slug = request.GET.get("area", "")

    if query:
        search_results = SupportTopicPage.objects.live().autocomplete(query)
    else:
        search_results = SupportTopicPage.objects.live().all()

    if area_slug:
        try:
            parent_page = Page.objects.get(slug=area_slug)
            search_results = (
                parent_page.get_descendants().live().public().filter(title__icontains=query)
            )
        except Page.DoesNotExist:
            search_results = Page.objects.none()

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)
