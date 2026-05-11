import datetime
import logging
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from wagtailcache.cache import WagtailCacheMixin, clear_cache

from .blocks import DocumentationPanel, _body_blocks
from .colors import LABEL_COLOR_CHOICES, THEME_COLOR_CHOICES

logger = logging.getLogger(__name__)


@register_snippet
class Label(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(
        max_length=20,
        choices=LABEL_COLOR_CHOICES,
        default="nceo-purple",
    )

    panels: ClassVar[list] = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("color"),
    ]

    SLUG_MAX_LENGTH = 50

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base = slugify(self.name)
        if not base:
            base = "label"
        slug = base[: self.SLUG_MAX_LENGTH]
        num = 1
        while Label.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix = f"-{num}"
            slug = f"{base[: self.SLUG_MAX_LENGTH - len(suffix)]}{suffix}"
            num += 1
        return slug

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering: ClassVar[list[str]] = ["name"]


@receiver(post_save, sender=Label)
@receiver(post_delete, sender=Label)
def purge_cache_on_label_change(sender: type, **kwargs: object) -> None:
    """Purge the entire wagtailcache when a Label snippet changes.

    Labels are rendered across many pages via template tags, so any
    change must invalidate all cached page output.
    """
    clear_cache()


# ---------------------------------------------------------------------
#  Notification Banner
# ---------------------------------------------------------------------
class NotificationBannerQuerySet(models.QuerySet):
    def active(self, now: datetime.datetime | None = None) -> "NotificationBannerQuerySet":
        if now is None:
            now = timezone.now()
        return (
            self.filter(is_enabled=True)
            .filter(models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now))
            .filter(models.Q(ends_at__isnull=True) | models.Q(ends_at__gt=now))
            .order_by("-priority", "starts_at", "title")
        )


@register_snippet
class NotificationBanner(models.Model):
    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    title = models.CharField(max_length=100, blank=True, help_text="Short optional label, e.g. 'Maintenance'")
    message = RichTextField(
        features=["bold", "italic", "link", "ol", "ul"],
        help_text="Banner message content (basic formatting and links only)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="info",
    )
    link_text = models.CharField(max_length=100, blank=True, help_text="Optional CTA text")
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional internal Wagtail page link",
    )
    link_url = models.URLField(blank=True, help_text="Optional external URL")
    starts_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the banner should start showing. Times are stored in UTC.",
    )
    ends_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the banner should stop showing. Times are stored in UTC.",
    )
    is_enabled = models.BooleanField(default=True, help_text="Enable or disable this banner")
    priority = models.IntegerField(default=0, help_text="Higher values win when multiple banners are active")
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotificationBannerQuerySet.as_manager()

    panels: ClassVar[list] = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("message"),
                FieldPanel("status"),
            ],
            heading="Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("link_text"),
                FieldPanel("link_page"),
                FieldPanel("link_url"),
            ],
            heading="Link",
        ),
        MultiFieldPanel(
            [
                FieldPanel("starts_at"),
                FieldPanel("ends_at"),
                FieldPanel("is_enabled"),
                FieldPanel("priority"),
            ],
            heading="Scheduling",
        ),
    ]

    class Meta:
        ordering: ClassVar[list[str]] = ["-priority", "starts_at", "title"]

    def __str__(self) -> str:
        return self.title or f"Banner {self.pk}"

    def is_active(self, now: datetime.datetime | None = None) -> bool:
        if now is None:
            now = timezone.now()
        if not self.is_enabled:
            return False
        if self.starts_at is not None and self.starts_at > now:
            return False
        if self.ends_at is not None and self.ends_at <= now:
            return False
        return True

    def clean(self) -> None:
        super().clean()
        errors: dict[str, ValidationError] = {}
        if self.link_page_id and self.link_url:
            errors["link_page"] = ValidationError("Cannot set both an internal page and an external URL.")
            errors["link_url"] = ValidationError("Cannot set both an internal page and an external URL.")
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = ValidationError("End time must be after start time.")
        if errors:
            raise ValidationError(errors)

    @classmethod
    def get_active_banner(cls) -> "NotificationBanner | None":
        """Return the highest-priority active banner, or None."""
        now = timezone.now()
        banner = cls.objects.active(now).first()
        if banner is None:
            logger.debug("No active notification banner at %s", now)
        else:
            logger.debug(
                "Active notification banner: id=%s title=%r starts_at=%s ends_at=%s",
                banner.pk,
                banner.title,
                banner.starts_at,
                banner.ends_at,
            )
        return banner

    @classmethod
    def get_next_boundary(cls, now: datetime.datetime | None = None) -> datetime.datetime | None:
        """Return the nearest future starts_at or ends_at among enabled banners.

        Used to decide whether it is safe to cache a page response: if the
        boundary is closer than the cache timeout, the response should not be
        cached so the banner state can refresh on time.
        """
        if now is None:
            now = timezone.now()

        future_start = (
            cls.objects.filter(is_enabled=True, starts_at__gt=now).aggregate(min=models.Min("starts_at")).get("min")
        )
        future_end = (
            cls.objects.filter(is_enabled=True, ends_at__gt=now)
            .filter(models.Q(starts_at__isnull=True) | models.Q(starts_at__lte=now))
            .aggregate(min=models.Min("ends_at"))
            .get("min")
        )

        boundaries = [b for b in (future_start, future_end) if b is not None]
        return min(boundaries) if boundaries else None


@receiver(post_save, sender=NotificationBanner)
@receiver(post_delete, sender=NotificationBanner)
def purge_cache_on_notification_banner_change(sender: type, **kwargs: object) -> None:
    """Purge the entire wagtailcache when a NotificationBanner snippet changes.

    Banners are rendered globally across all pages via a context processor,
    so any change must invalidate all cached page output.
    """
    clear_cache()


# ---------------------------------------------------------------------
#  Home Page (Site Root)
# ---------------------------------------------------------------------
class HomePage(WagtailCacheMixin, Page):
    overview_text = RichTextField(blank=True, default="Welcome to our website!")

    aim_1_title = models.CharField(max_length=255, blank=True, default="Our First Aim")
    aim_1_description = RichTextField(blank=True, default="Description of our first aim.")
    aim_1_image = models.ImageField(upload_to="aims/", blank=True, null=True)
    aim_1_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional internal page link for this card",
    )

    aim_2_title = models.CharField(max_length=255, blank=True, default="Our Second Aim")
    aim_2_description = RichTextField(blank=True, default="Description of our second aim.")
    aim_2_image = models.ImageField(upload_to="aims/", blank=True, null=True)
    aim_2_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional internal page link for this card",
    )

    aim_3_title = models.CharField(max_length=255, blank=True, default="Our Third Aim")
    aim_3_description = RichTextField(blank=True, default="Description of our third aim.")
    aim_3_image = models.ImageField(upload_to="aims/", blank=True, null=True)
    aim_3_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional internal page link for this card",
    )

    aim_4_title = models.CharField(max_length=255, blank=True, default="Our Fourth Aim")
    aim_4_description = RichTextField(blank=True, default="Description of our fourth aim.")
    aim_4_image = models.ImageField(upload_to="aims/", blank=True, null=True)
    aim_4_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional internal page link for this card",
    )

    content_panels: ClassVar[list] = Page.content_panels + [
        FieldPanel("overview_text"),
        MultiFieldPanel(
            [
                FieldPanel("aim_1_title"),
                FieldPanel("aim_1_description"),
                FieldPanel("aim_1_image"),
                FieldPanel("aim_1_page"),
            ],
            heading="Aim 1",
            classname="collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("aim_2_title"),
                FieldPanel("aim_2_description"),
                FieldPanel("aim_2_image"),
                FieldPanel("aim_2_page"),
            ],
            heading="Aim 2",
            classname="collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("aim_3_title"),
                FieldPanel("aim_3_description"),
                FieldPanel("aim_3_image"),
                FieldPanel("aim_3_page"),
            ],
            heading="Aim 3",
            classname="collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("aim_4_title"),
                FieldPanel("aim_4_description"),
                FieldPanel("aim_4_image"),
                FieldPanel("aim_4_page"),
            ],
            heading="Aim 4",
            classname="collapsed",
        ),
    ]


# ---------------------------------------------------------------------
#  Landing Page Mixin (shared fields for index pages)
# ---------------------------------------------------------------------
class LandingPageMixin(models.Model):
    """Shared content fields for section index / landing pages."""

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Main hero or banner image for the top of the page.",
    )
    hero_caption = models.TextField(
        blank=True,
        help_text="Caption or alt-text for the hero image. Press Enter for a new line.",
    )
    intro = RichTextField(blank=True, help_text="A short intro paragraph below the title.")
    intro_background_color = models.CharField(
        max_length=20,
        choices=THEME_COLOR_CHOICES,
        default="default",
        blank=True,
        help_text="Background color for the intro section.",
    )
    intro_full_width_background = models.BooleanField(
        default=False,
        help_text="Stretch the intro background to the full width of the page.",
    )

    class Meta:
        abstract = True

    # Panels defined as a classmethod so subclasses can include them
    # in their own content_panels. The body StreamField is declared on
    # each concrete model because it references block classes defined
    # in blocks.py.

    @classmethod
    def landing_panels(cls) -> list:
        return [
            MultiFieldPanel(
                [
                    FieldPanel("hero_image"),
                    FieldPanel("hero_caption"),
                ],
                heading="Hero Image",
                classname="collapsed",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("intro"),
                    MultiFieldPanel(
                        [
                            FieldPanel("intro_background_color"),
                            FieldPanel("intro_full_width_background"),
                        ],
                        heading="Intro Style",
                        classname="collapsed",
                    ),
                ],
                heading="Intro",
            ),
            FieldPanel("body"),
        ]


# ---------------------------------------------------------------------
#  About Section
# ---------------------------------------------------------------------
class AboutIndexPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    /about/ landing page.
    Contains subpages: HubPage, ApplicationsPage, AccessPage
    """

    template = "home/landing_page.html"

    body = StreamField(_body_blocks(), blank=True)

    content_panels: ClassVar[list] = Page.content_panels + LandingPageMixin.landing_panels()

    subpage_types: ClassVar[list[str]] = ["GenericPage"]
    parent_page_types: ClassVar[list[str]] = ["HomePage"]


# ---------------------------------------------------------------------
#  Data Section
# ---------------------------------------------------------------------
class DataIndexPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    /data/ landing page.
    Contains: OpenAccessPage, CommercialPage
    """

    template = "home/landing_page.html"

    body = StreamField(_body_blocks(), blank=True)

    content_panels: ClassVar[list] = Page.content_panels + LandingPageMixin.landing_panels()

    subpage_types: ClassVar[list[str]] = ["GenericPage"]
    parent_page_types: ClassVar[list[str]] = ["HomePage"]


# ---------------------------------------------------------------------
#  Docs Section (Getting Started)
# ---------------------------------------------------------------------
class DocsIndexPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    /docs/ landing page.
    Contains: AccountSetupPage, FAQPage, DocumentationPage
    """

    template = "home/landing_page.html"

    body = StreamField(_body_blocks(), blank=True)

    content_panels: ClassVar[list] = Page.content_panels + LandingPageMixin.landing_panels()

    subpage_types: ClassVar[list[str]] = ["DocumentationPage"]
    parent_page_types: ClassVar[list[str]] = ["HomePage"]


class DocumentationPage(WagtailCacheMixin, Page):
    """
    /docs/documentation/ page.
    Contains: GenericPage
    """

    intro = RichTextField(blank=True)
    intro_background_color = models.CharField(
        max_length=20,
        choices=THEME_COLOR_CHOICES,
        default="default",
        blank=True,
        help_text="Background color for the intro section.",
    )
    intro_full_width_background = models.BooleanField(
        default=False,
        help_text="Stretch the intro background to the full width of the page.",
    )

    topics = StreamField(
        [("documentation_panel", DocumentationPanel())],
        blank=True,
        help_text="Add documentation panels to this page.",
    )
    topics_background_color = models.CharField(
        max_length=20,
        choices=THEME_COLOR_CHOICES,
        default="default",
        blank=True,
        help_text="Background color for the topics grid section.",
    )
    topics_full_width_background = models.BooleanField(
        default=False,
        help_text="Stretch the topics background to the full width of the page.",
    )
    topics_show_filter = models.BooleanField(
        default=False,
        help_text="Show a label filter bar above the topic cards.",
    )

    content_panels: ClassVar[list] = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("intro"),
                MultiFieldPanel(
                    [
                        FieldPanel("intro_background_color"),
                        FieldPanel("intro_full_width_background"),
                    ],
                    heading="Intro Style",
                    classname="collapsed",
                ),
            ],
            heading="Intro",
        ),
        MultiFieldPanel(
            [
                FieldPanel("topics"),
                MultiFieldPanel(
                    [
                        FieldPanel("topics_background_color"),
                        FieldPanel("topics_full_width_background"),
                        FieldPanel("topics_show_filter"),
                    ],
                    heading="Topics Style",
                    classname="collapsed",
                ),
            ],
            heading="Topics",
        ),
    ]

    subpage_types: ClassVar[list[str]] = ["GenericPage"]
    parent_page_types: ClassVar[list[str]] = ["DocsIndexPage"]


# ---------------------------------------------------------------------
#  Case Studies Section
# ---------------------------------------------------------------------
class CaseStudiesPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    /case-studies/ landing page.
    Contains: CaseStudyPage
    """

    template = "home/landing_page.html"

    body = StreamField(_body_blocks(), blank=True)

    content_panels: ClassVar[list] = Page.content_panels + LandingPageMixin.landing_panels()

    subpage_types: ClassVar[list[str]] = ["GenericPage"]
    parent_page_types: ClassVar[list[str]] = ["HomePage"]


# ---------------------------------------------------------------------
#  Catalogue Section
# ---------------------------------------------------------------------
class CatalogueIndexPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    /catalogue/ landing page.
    """

    template = "home/landing_page.html"

    body = StreamField(_body_blocks(), blank=True)

    content_panels: ClassVar[list] = Page.content_panels + LandingPageMixin.landing_panels()

    subpage_types: ClassVar[list[str]] = ["GenericPage"]
    parent_page_types: ClassVar[list[str]] = ["HomePage"]


# ---------------------------------------------------------------------
#  Generic Page (flexible content page used throughout the site)
# ---------------------------------------------------------------------
class GenericPage(LandingPageMixin, WagtailCacheMixin, Page):
    """
    We can use this as a generic page type for any page.
    """

    body = StreamField(_body_blocks(), blank=True)

    back_button_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="URL to redirect to when the back button is clicked",
    )

    content_panels: ClassVar[list] = (
        Page.content_panels
        + LandingPageMixin.landing_panels()
        + [
            FieldPanel("back_button_location"),
        ]
    )

    parent_page_types: ClassVar[list[str]] = [
        "AboutIndexPage",
        "CatalogueIndexPage",
        "DataIndexPage",
        "DocsIndexPage",
        "CaseStudiesPage",
        "DocumentationPage",
        "HomePage",
        "GenericPage",
    ]
    subpage_types: ClassVar[list[str]] = ["GenericPage"]

    class Meta:
        verbose_name = "Generic Page"
        verbose_name_plural = "Generic Pages"
