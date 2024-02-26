from django.shortcuts import render

from eodhp_web_presence import settings


def catalogue_page_view(request):
    context = {"url": settings.STAC_BROWSER["url"]}
    return render(request, "catalogue/catalogue_page.html", context=context)
