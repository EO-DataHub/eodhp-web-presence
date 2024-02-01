from django.db.models import CharField, DateField
from wagtail.models import Page


class CataloguePage(Page):
    content_panels = Page.content_panels
