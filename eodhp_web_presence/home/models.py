from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ContentBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, help_text="Optional heading")
    paragraph = blocks.RichTextBlock(required=False)
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = "doc-full"
        label = "Content Block"
        template = "blocks/content_block.html"
        help_text = "Use this block to create flexible content sections."


class GenericPage(WagtailCacheMixin, Page):
    """
    We can use this as a generic page type for any page.
    """

    # Hero / banner
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Main hero or banner image for the top of the page.",
    )
    hero_caption = models.CharField(
        max_length=255, blank=True, help_text="Caption or alt-text for the hero image"
    )

    intro = RichTextField(
        blank=True, help_text="A short intro paragraph that sits below the title/subtitle."
    )

    body = StreamField(
        [
            ("content_block", ContentBlock()),
            ("blockquote", blocks.BlockQuoteBlock()),
            ("raw_html", blocks.RawHTMLBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    cta_text = models.CharField(max_length=255, blank=True, help_text="Button or link text")
    cta_url = models.URLField(blank=True, help_text="Target URL for the call-to-action")

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_caption"),
            ],
            heading="Hero Image",
        ),
        MultiFieldPanel(
            [
                FieldPanel("intro"),
            ],
            heading="Intro",
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("cta_text"),
                FieldPanel("cta_url"),
            ],
            heading="Call to Action",
        ),
    ]

    parent_page_types = [
        "AboutIndexPage",
        "DataIndexPage",
        "DocsIndexPage",
        "CaseStudiesPage",
        "DocumentationPage",
    ]
    subpage_types = []

    class Meta:
        verbose_name = "Generic Page"
        verbose_name_plural = "Generic Pages"


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

    subpage_types = ["GenericPage"]
    parent_page_types = ["HomePage"]


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

    subpage_types = ["GenericPage"]
    parent_page_types = ["HomePage"]


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

    subpage_types = ["DocumentationPage"]
    parent_page_types = ["HomePage"]


class DocumentationPanel(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Title of the documentation panel")
    slug = blocks.CharBlock(
        required=True,
        help_text="Unique identifier in the url e.g. workflow",
        max_length=50,
    )
    description = blocks.RichTextBlock(
        required=True, help_text="Description of the documentation panel"
    )
    image = ImageChooserBlock(
        required=False, help_text="Optional image for the documentation panel"
    )

    class Meta:
        icon = "doc-full"
        label = "Documentation Panel"
        template = "blocks/documentation_panel.html"
        help_text = "Use this block to create documentation panels with title, description, and optional image."


class DocumentationPage(WagtailCacheMixin, Page):
    """
    /docs/documentation/ page.
    Contains: GenericPage
    """

    intro = RichTextField(blank=True)

    topics = StreamField(
        [("documentation_panel", DocumentationPanel())],
        blank=True,
        use_json_field=True,
        help_text="Add documentation panels to this page.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("topics"),
    ]

    subpage_types = ["GenericPage"]
    parent_page_types = ["DocsIndexPage"]


# ---------------------------------------------------------------------
#  Case Studies Section
# ---------------------------------------------------------------------
class CaseStudiesPage(WagtailCacheMixin, Page):
    """
    /case-studies/ index.
    Contains: CaseStudyPage
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["GenericPage"]
    parent_page_types = ["HomePage"]
