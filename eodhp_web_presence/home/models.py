from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin


class HomePage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True)

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    about_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    contact_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    news_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("banner_image"),
        FieldPanel("image"),
        FieldPanel("about_image"),
        FieldPanel("contact_image"),
        FieldPanel("news_image"),
    ]


class AboutPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True)

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
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
        FieldPanel("banner_image"),
        FieldPanel("image"),
    ]

    template = "home/about_page.html"


class NewsPage(WagtailCacheMixin, Page):
    # Can only have NewsArticlePage children
    subpage_types = ["NewsArticlePage"]

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    template = "home/news_page.html"

    # Returns a queryset of NewsArticlePage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_news_articles(self):
        return (
            NewsArticlePage.objects.live()  # .descendant_of(self).order_by("-first_published_at")
        )

    def get_banner_image(self):
        if self.banner_image:
            return self.banner_image
        return None

    # Allows child objects (e.g. NewsArticlePage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    # Pagination for the index page. We use the `django.core.paginator` as any
    # standard Django app would, but the difference here being we have it as a
    # method on the model rather than within a view function
    def paginate(self, request, *args):
        page = request.GET.get("page")
        paginator = Paginator(self.get_news_articles(), 12)
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
        context = super(NewsPage, self).get_context(request)

        # NewsArticlePage objects (get_news_articles) are passed through pagination
        # news_articles = self.paginate(request, self.get_news_articles())
        news_articles = self.get_news_articles()

        context["news_articles"] = news_articles

        return context

    content_panels = Page.content_panels + [
        FieldPanel("banner_image"),
    ]


class NewsArticlePage(WagtailCacheMixin, Page):
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

    template = "home/news_article_page.html"


class ContactPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True)

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("banner_image"),
    ]

    template = "home/contact_page.html"


class CataloguePage(Page):
    content_panels = Page.content_panels


class FakeCataloguePage(WagtailCacheMixin, Page):
    content_panels = Page.content_panels

    template = "fake-catalogue/map-search.html"
