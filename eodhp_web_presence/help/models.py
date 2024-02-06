# Create your models here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import CharField, DateField
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import RichTextField
from wagtail.models import Page


class HelpPage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class HelpIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ["HelpPage"]

    subtitle = CharField(blank=True, max_length=255)
    date_published = DateField("Date article published", blank=True, null=True)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return the updated context
        context['blog_entries'] = HelpPage.objects.child_of(self).live()
        return context
