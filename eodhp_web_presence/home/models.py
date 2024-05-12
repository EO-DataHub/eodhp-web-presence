from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import ForeignKey, CASCADE
from django.forms import CharField, DateField
from django.shortcuts import render
from wagtail import blocks
from wagtail.admin import widgets
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.blocks import BaseStreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import AbstractImage, Image
from wagtail.models import Page
from django.db import models
from wagtail.templatetags import wagtailcore_tags
from datetime import date

from eodhp_web_presence import settings


# class CustomImage(AbstractImage):
#     # Add any extra fields to image here
#
#     # To add a caption field:
#     # caption = models.CharField(max_length=255, blank=True)
#
#     admin_form_fields = Image.admin_form_fields + (
#         # Then add the field names here to make them appear in the form:
#         # 'caption',
#     )

class HomePage(Page):
    body = RichTextField(blank=True)


    image = models.ForeignKey(
            "wagtailimages.Image",
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="+",
            help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
        )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("image"),
    ]

    # print('AAAAAAAAAAAAAAAA')
    # print(Page.__dict__)
    # def serve(self, request):
    #     context = {
    #         "resource_catalogue_url": "/catalogue",
    #         "eox_viewserver_url": settings.EOX_VIEWSERVER["url"],
    #         "documentation_url": settings.DOCUMENTATION["url"],
    #         "notebooks_url": settings.NOTEBOOKS["url"],
    #     }
    #
    #     return render(request, "home/home_page.html", context=context)


class AboutPage(Page):
    body = RichTextField(blank=True)

    image = models.ForeignKey(
            "wagtailimages.Image",
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="+",
            help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
        )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("image"),
    ]

    template = "home/about_page.html"


class AnnouncementsPage(Page):

    # image = models.ForeignKey(
    #     "wagtailimages.Image",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="+",
    #     help_text="Landscape mode only; horizontal width between 1000px and " "3000px.",
    # )

    # content_panels = Page.content_panels + [
    #     FieldPanel("image"),
    # ]

    # Can only have AnnouncementPage children
    subpage_types = ["AnnouncementPage"]

    template = "home/announcements_page.html"

    # Returns a queryset of AnnouncementPage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_announcements(self):
        return (
            AnnouncementPage.objects.live()#.descendant_of(self).order_by("-first_published_at")
        )

    # Allows child objects (e.g. AnnouncementPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    # Pagination for the index page. We use the `django.core.paginator` as any
    # standard Django app would, but the difference here being we have it as a
    # method on the model rather than within a view function
    def paginate(self, request, *args):
        page = request.GET.get("page")
        paginator = Paginator(self.get_announcements(), 12)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages

    # Returns the above to the get_context method that is used to populate the
    # template
    def get_context(self, request):
        context = super(AnnouncementsPage, self).get_context(request)

        # BreadPage objects (get_breads) are passed through pagination
        # announcements = self.paginate(request, self.get_announcements())
        announcements = self.get_announcements()

        context["announcements"] = announcements

        return context


    # content_panels = Page.content_panels
    #
    # subpage_types = ["AnnouncementPage"]
    #
    # subtitle = CharField()
    # date_published = DateField()
    #
    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #
    #     # Add extra variables and return the updated context
    #     context["announcement_entries"] = AnnouncementPage.objects.child_of(self).live()
    #     return context


class AnnouncementPage(Page):
    body = RichTextField(blank=True, default="")
    summary = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # body = StreamField([
    # # ('announcement', blocks.StructBlock([
    # #     ('introduction', blocks.CharBlock()),
    # #     ('image', ImageChooserBlock(required=False)),
    # #     ('body', blocks.RichTextBlock()),
    # # ], icon='user')),
    #     ('introduction', blocks.CharBlock(form_classname="title")),
    #     ('body', blocks.RichTextBlock()),
    #     ('image', ImageChooserBlock()),
    # ],  verbose_name="Page body", blank=True, use_json_field=True, null=True)
    # #     BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    # # )



    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]

    template = "home/announcement_page.html"

    # def full_clean(self, *args, **kwargs):
    #     if not self.slug.startswith('announcements/'):
    #         self.slug = 'announcements/' + self.slug
    #     super().full_clean(*args, **kwargs)


class ContactPage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


    template = "home/contact_page.html"
