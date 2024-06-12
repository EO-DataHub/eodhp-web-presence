from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin


class HomePage(WagtailCacheMixin, Page):
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


class AboutPage(WagtailCacheMixin, Page):
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


class AnnouncementsPage(WagtailCacheMixin, Page):
    # Can only have AnnouncementPage children
    subpage_types = ["AnnouncementPage"]

    template = "home/announcements_page.html"

    # Returns a queryset of AnnouncementPage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_announcements(self):
        return (
            AnnouncementPage.objects.live()  # .descendant_of(self).order_by("-first_published_at")
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

        # AnnouncementPage objects (get_accounecements) are passed through pagination
        # announcements = self.paginate(request, self.get_announcements())
        announcements = self.get_announcements()

        context["announcements"] = announcements

        return context


class AnnouncementPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True, default="")
    summary = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]

    template = "home/announcement_page.html"


class ContactPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    template = "home/contact_page.html"


class AccessPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    template = "home/access_page.html"