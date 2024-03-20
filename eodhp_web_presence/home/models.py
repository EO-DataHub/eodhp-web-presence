from django.shortcuts import render
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from eodhp_web_presence import settings


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def serve(self, request):
        context = {
            "resource_catalogue_url": "/catalogue",
            "eox_viewserver_url": settings.EOX_VIEWSERVER["url"],
            "documentation_url": settings.DOCUMENTATION["url"],
            "notebooks_url": settings.NOTEBOOKS["url"],
        }

        return render(request, "home/home_page.html", context=context)
