from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin


# ---------------------------------------------------------------------
#  Home Page (Site Root)
# ---------------------------------------------------------------------
class HomePage(WagtailCacheMixin, Page):
    overview_text = RichTextField(blank=True, default="Welcome to our website!")

    aim_1_title = models.CharField(max_length=255, blank=True, default="Our First Aim")
    aim_1_description = RichTextField(blank=True, default="Description of our first aim.")
    aim_1_image = models.ImageField(upload_to="aims/", blank=True, null=True)

    aim_2_title = models.CharField(max_length=255, blank=True, default="Our Second Aim")
    aim_2_description = RichTextField(blank=True, default="Description of our second aim.")
    aim_2_image = models.ImageField(upload_to="aims/", blank=True, null=True)

    aim_3_title = models.CharField(max_length=255, blank=True, default="Our Third Aim")
    aim_3_description = RichTextField(blank=True, default="Description of our third aim.")
    aim_3_image = models.ImageField(upload_to="aims/", blank=True, null=True)

    aim_4_title = models.CharField(max_length=255, blank=True, default="Our Fourth Aim")
    aim_4_description = RichTextField(blank=True, default="Description of our fourth aim.")
    aim_4_image = models.ImageField(upload_to="aims/", blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview_text"),
        FieldPanel("aim_1_title"),
        FieldPanel("aim_1_description"),
        FieldPanel("aim_1_image"),
        FieldPanel("aim_2_title"),
        FieldPanel("aim_2_description"),
        FieldPanel("aim_2_image"),
        FieldPanel("aim_3_title"),
        FieldPanel("aim_3_description"),
        FieldPanel("aim_3_image"),
        FieldPanel("aim_4_title"),
        FieldPanel("aim_4_description"),
        FieldPanel("aim_4_image"),
    ]


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
