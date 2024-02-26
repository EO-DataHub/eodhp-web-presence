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
        context = {"eoxserver_url": settings.ENVIRONMENT["eoxserver"]}

        return render(request, "home/home_page.html", context=context)
