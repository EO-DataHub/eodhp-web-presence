from django.db.models import CharField, DateField

from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import RichTextField
from wagtail.models import Page
from django.db import models

from .views import help_page_view


class HelpPage(Page):

    content_panels = Page.content_panels


    subtitle = CharField(blank=True, max_length=255)
    date_published = DateField("Date article published", blank=True, null=True)


    # title = models.TextField(help_text="Help and Support", blank=True)
    # introduction = models.TextField(help_text="Information and troubleshooting", blank=True)

    # body = RichTextField()
    # date = models.DateField("Post date")


    # subtitle = CharField(blank=True, max_length=255)
    # date_published = DateField("Date article published", blank=True, null=True)

    # body = RichTextField()
    # date = models.DateField("Post date")
    # feed_image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )


    # class Meta:
    #     verbose_name = "Help or support page"
#
#
# HelpPage.content_panels = [
#     FieldPanel('title', classname="full title"),
#     FieldPanel('date'),
#     FieldPanel('body', classname="full"),
# ]
#
# HelpPage.promote_panels = [
#     FieldPanel('slug'),
#     FieldPanel('seo_title'),
#     FieldPanel('show_in_menus'),
#     FieldPanel('search_description'),
#     # ImageChooserPanel('feed_image'),
# ]


    # def serve(self, request, *args, **kwargs):
    #     return help_page_view(request)

    # def get_admin_display_title(self):
    #     print('SDSSSSSSSSSSSSSSSSSSSSSSs')
    #     return "Custom Home Page Title"
