from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from wagtail.models import Page

from eodhp_web_presence import settings

from .models import SupportAreaPage, SupportTopicPage


def catalogue_page_view(request):
    resource_catalogue_version = settings.RESOURCE_CATALOGUE["version"]
    resource_catalogue_base_url = settings.RESOURCE_CATALOGUE["url"]
    resource_catalogue_url = f"{resource_catalogue_base_url}/{resource_catalogue_version}"
    context = {"url": resource_catalogue_url, "catalogue_data_url": settings.CATALOGUE_DATA["url"]}

    return render(request, "home/catalogue_page.html", context=context)


def search_topics(request):
    query = request.GET.get("query", "")
    area_slug = request.GET.get("area", "")

    if area_slug:
        try:
            area_page = SupportAreaPage.objects.get(slug=area_slug)
            search_results = SupportTopicPage.objects.child_of(area_page).live().autocomplete(query)
        except Page.DoesNotExist:
            search_results = Page.objects.none()

    else:
        if query:
            search_results = SupportTopicPage.objects.live().autocomplete(query)
        else:
            search_results = SupportTopicPage.objects.live().all()

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)
