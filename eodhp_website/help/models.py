from django.db.models import CharField, DateField
from wagtail.models import Page


class HelpPage(Page):
    content_panels = Page.content_panels

    subtitle = CharField(blank=True, max_length=255)
    date_published = DateField("Date article published", blank=True, null=True)
