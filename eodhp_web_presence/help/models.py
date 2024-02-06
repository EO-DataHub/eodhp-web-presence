from datetime import date

from django.db.models import DateField
from wagtail.admin import widgets
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HelpPage(Page):
    date = DateField("Date", blank=True, null=True, default=date.today)
    body = RichTextField(blank=True)

    date_widget = widgets.AdminDateInput(attrs={"placeholder": "dd-mm-yyyy"})

    content_panels = Page.content_panels + [
        FieldPanel("date", widget=date_widget),
        FieldPanel("body"),
    ]

    parent_page_types = ["help.HelpIndexPage"]


class HelpIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ["HelpPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return the updated context
        context["entries"] = HelpPage.objects.child_of(self).live()
        return context
