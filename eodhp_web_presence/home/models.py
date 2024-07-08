from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import TextField
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

    video_url = TextField(blank=True)

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
        FieldPanel("video_url"),
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
        ).reverse()

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


class SupportIndexPage(WagtailCacheMixin, Page):
    # Can only have SupportAreaPage children
    subpage_types = ["SupportAreaPage"]

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    template = "home/support_index_page.html"

    # Returns a queryset of SupportAreaPage objects that are live, that are direct
    # descendants of this index page with most recent first
    def get_support_areas(self):
        return (
            SupportAreaPage.objects.live()  # .descendant_of(self).order_by("-first_published_at")
        )

    def get_banner_image(self):
        if self.banner_image:
            return self.banner_image
        return None

    # Allows child objects (e.g. SupportAreaPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    # Pagination for the index page. We use the `django.core.paginator` as any
    # standard Django app would, but the difference here being we have it as a
    # method on the model rather than within a view function
    def paginate(self, request, *args):
        page = request.GET.get("page")
        paginator = Paginator(self.get_support_areas(), 12)
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
        context = super(SupportIndexPage, self).get_context(request)

        # SupportAreaPage objects (get_support_areas) are passed through pagination
        support_areas = self.get_support_areas()
        context["support_areas"] = support_areas

        support_topics = self.children().type(SupportTopicPage)
        context["support_topics"] = support_topics

        return context

    content_panels = Page.content_panels + [
        FieldPanel("banner_image"),
    ]


class SupportAreaPage(WagtailCacheMixin, Page):
    # Can only have SupportTopicPage children
    subpage_types = ["SupportTopicPage", "SupportFAQPage"]

    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    template = "home/support_area_page.html"

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
        paginator = Paginator(self.get_help_areas(), 12)
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
        context = super(SupportAreaPage, self).get_context(request)

        support_topics = self.children().type(SupportTopicPage)
        support_faqs = self.children().type(SupportFAQPage)

        context["support_topics"] = support_topics
        context["support_faqs"] = support_faqs

        return context

    content_panels = Page.content_panels + [
        FieldPanel("banner_image"),
        FieldPanel("image"),
    ]


class SupportTopicPage(WagtailCacheMixin, Page):
    body = RichTextField(blank=True, default="")

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        FieldPanel("image"),
        FieldPanel("body"),
    ]

    template = "home/support_topic_page.html"


class SupportFAQPage(WagtailCacheMixin, Page):
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
    ]

    # template = "home/news_article_page.html"
