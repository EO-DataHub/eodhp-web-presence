from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin


# ---------------------------------------------------------------------
#  Home Page (Site Root)
# ---------------------------------------------------------------------
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
    video_url = models.TextField(blank=True)
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

    # subpage_types = ["AboutIndexPage", "DataIndexPage", "DocsIndexPage"]
    # parent_page_types = []


# ---------------------------------------------------------------------
#  About Section
# ---------------------------------------------------------------------
class AboutIndexPage(WagtailCacheMixin, Page):
    """
    Acts like /about/ index.
    Contains subpages: HubPage, ApplicationsPage, AccessPage
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["HubPage", "ApplicationsPage", "AccessPage"]
    parent_page_types = ["HomePage"]


class HubPage(WagtailCacheMixin, Page):
    """
    /about/hub
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["AboutIndexPage"]
    subpage_types = []


class ApplicationsPage(WagtailCacheMixin, Page):
    """
    /about/applications
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["AboutIndexPage"]
    subpage_types = []


class AccessPage(WagtailCacheMixin, Page):
    """
    /about/access
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["AboutIndexPage"]
    subpage_types = []


# ---------------------------------------------------------------------
#  Data Section
# ---------------------------------------------------------------------
class DataIndexPage(WagtailCacheMixin, Page):
    """
    /data/ index.
    Contains: OpenAccessPage, CommercialPage
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["OpenAccessPage", "CommercialPage"]
    parent_page_types = ["HomePage"]


class OpenAccessPage(WagtailCacheMixin, Page):
    """
    /data/open-access
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["DataIndexPage"]
    subpage_types = []


class CommercialPage(WagtailCacheMixin, Page):
    """
    /data/commercial
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["DataIndexPage"]
    subpage_types = []


# ---------------------------------------------------------------------
#  Docs Section (Getting Started)
# ---------------------------------------------------------------------
class DocsIndexPage(WagtailCacheMixin, Page):
    """
    /docs/ index.
    Contains: AccountSetupPage, FAQPage, DocumentationPage
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["AccountSetupPage", "FAQPage", "DocumentationPage"]
    parent_page_types = ["HomePage"]


class AccountSetupPage(WagtailCacheMixin, Page):
    """
    /docs/account-setup
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["DocsIndexPage"]
    subpage_types = []


class FAQPage(WagtailCacheMixin, Page):
    """
    /docs/faqs
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["DocsIndexPage"]
    subpage_types = []


class DocumentationPage(WagtailCacheMixin, Page):
    """
    /docs/documentation
    """

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["DocsIndexPage"]
    subpage_types = []
