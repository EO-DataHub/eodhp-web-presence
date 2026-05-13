from datetime import timedelta
from unittest.mock import patch

import pytest
from core.middleware import BannerCacheMiddleware
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.utils import timezone
from wagtail.models import Page, Site

from home.blocks import (
    AccordionBlock,
    AccordionItemBlock,
    BackgroundMixin,
    ColumnBlock,
    ContentBlock,
    CTABlock,
    DocumentationPanel,
    ImageBlock,
    LayoutMixin,
    MediaEmbedBlock,
    RowBlock,
    _body_blocks,
    _inner_blocks,
)
from home.models import (
    AboutIndexPage,
    CaseStudiesPage,
    CatalogueIndexPage,
    DataIndexPage,
    DocsIndexPage,
    DocumentationPage,
    GenericPage,
    HomePage,
    Label,
    NotificationBanner,
)


class LandingPageTestMixin:
    """Shared helpers for creating landing pages under the home page."""

    def setUp(self):
        super().setUp()
        self.root = Page.objects.get(depth=1)
        self.home = HomePage(title="Test Home", slug="testhome")
        self.root.add_child(instance=self.home)
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={"root_page": self.home, "hostname": "localhost"},
        )


@override_settings(WAGTAIL_CACHE=False)
class TestHomePage(LandingPageTestMixin, TestCase):
    def test_home_page_serves(self):
        response = self.client.get(self.home.url)
        assert response.status_code == 200

    def test_home_page_no_breadcrumbs(self):
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertNotContains(response, '<nav class="breadcrumbs"')

    def test_aim_page_links_render(self):
        """Aim cards with linked pages render an anchor tag."""
        target = GenericPage(title="Target", slug="target")
        self.home.add_child(instance=target)
        self.home.aim_1_page = target
        self.home.save()

        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, f'href="{target.url}"')


@override_settings(WAGTAIL_CACHE=False)
class TestLandingPages(LandingPageTestMixin, TestCase):
    """All landing page types should serve using the shared template."""

    page_classes = (
        AboutIndexPage,
        DataIndexPage,
        DocsIndexPage,
        CaseStudiesPage,
        CatalogueIndexPage,
    )

    def test_landing_pages_serve(self):
        for cls in self.page_classes:
            slug = cls.__name__.lower()
            page = cls(title=cls.__name__, slug=slug)
            self.home.add_child(instance=page)

            with self.subTest(page_type=cls.__name__):
                response = self.client.get(page.url)
                assert response.status_code == 200

    def test_landing_pages_use_shared_template(self):
        for cls in self.page_classes:
            slug = cls.__name__.lower()
            page = cls(title=cls.__name__, slug=slug)
            self.home.add_child(instance=page)

            with self.subTest(page_type=cls.__name__):
                response = self.client.get(page.url)
                self.assertTemplateUsed(response, "home/landing_page.html")
                self.assertTemplateUsed(response, "home/includes/landing_page_content.html")

    def test_landing_pages_render_breadcrumbs(self):
        for cls in self.page_classes:
            slug = cls.__name__.lower()
            page = cls(title=cls.__name__, slug=slug)
            self.home.add_child(instance=page)

            with self.subTest(page_type=cls.__name__):
                response = self.client.get(page.url)
                self.assertContains(response, '<nav class="breadcrumbs"')
                self.assertContains(response, f'<a href="{self.home.url}">{self.home.title}</a>')
                self.assertContains(response, f'<span aria-current="page">{cls.__name__}</span>')


@override_settings(WAGTAIL_CACHE=False)
class TestGenericPage(LandingPageTestMixin, TestCase):
    def test_generic_page_serves(self):
        page = GenericPage(title="Test Page", slug="test-page")
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200

    def test_generic_page_renders_breadcrumbs(self):
        page = GenericPage(title="Test Page", slug="test-page")
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        self.assertContains(response, '<nav class="breadcrumbs"')
        self.assertContains(response, f'<a href="{self.home.url}">{self.home.title}</a>')
        self.assertContains(response, '<span aria-current="page">Test Page</span>')

    def test_nested_generic_page_renders_full_ancestry(self):
        parent = GenericPage(title="Parent", slug="parent")
        self.home.add_child(instance=parent)
        child = GenericPage(title="Child", slug="child")
        parent.add_child(instance=child)

        response = self.client.get(child.url)
        self.assertContains(response, f'<a href="{self.home.url}">{self.home.title}</a>')
        self.assertContains(response, f'<a href="{parent.url}">Parent</a>')
        self.assertContains(response, '<span aria-current="page">Child</span>')

    def test_generic_page_with_topics_grid(self):
        page = GenericPage(
            title="Topics Page",
            slug="topics-page",
            body=[
                (
                    "topics_grid",
                    {
                        "background_color": "default",
                        "full_width_background": False,
                        "topics": [
                            {
                                "title": "My Topic",
                                "slug": "my-topic",
                                "description": "<p>A description</p>",
                                "image": None,
                                "featured_image": False,
                            }
                        ],
                    },
                )
            ],
        )
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        self.assertContains(response, "My Topic")

    def test_topics_grid_renders_page_scoped_links(self):
        """The topics_grid block template must see `page` to build slug links."""
        page = GenericPage(
            title="Topics Page",
            slug="topics-page-links",
            body=[
                (
                    "topics_grid",
                    {
                        "topics": [
                            {
                                "title": "T",
                                "slug": "my-topic",
                                "description": "<p>d</p>",
                                "image": None,
                                "featured_image": False,
                            }
                        ],
                    },
                )
            ],
        )
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        self.assertContains(response, f'href="{page.url}my-topic"')

    def test_generic_page_cta_in_body(self):
        """CTA blocks render inside the body streamfield."""
        page = GenericPage(
            title="CTA Page",
            slug="cta-page",
            body=[
                (
                    "cta",
                    {
                        "text": "Sign Up Now",
                        "link_url": "https://example.com/signup",
                    },
                )
            ],
        )
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        self.assertContains(response, "Sign Up Now")
        self.assertContains(response, "primary-button")


@override_settings(WAGTAIL_CACHE=False)
class TestDocumentationPage(LandingPageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.docs_index = DocsIndexPage(title="Docs", slug="docs")
        self.home.add_child(instance=self.docs_index)

    def test_documentation_page_serves(self):
        page = DocumentationPage(title="Documentation", slug="documentation")
        self.docs_index.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200

    def test_documentation_page_renders_breadcrumbs(self):
        page = DocumentationPage(title="Documentation", slug="documentation")
        self.docs_index.add_child(instance=page)

        response = self.client.get(page.url)
        self.assertContains(response, '<nav class="breadcrumbs"')
        self.assertContains(response, f'<a href="{self.home.url}">{self.home.title}</a>')
        self.assertContains(response, f'<a href="{self.docs_index.url}">Docs</a>')
        self.assertContains(response, '<span aria-current="page">Documentation</span>')

    def test_featured_image_card_class(self):
        """When featured_image is true but no image, the featured variant should not render."""
        page = DocumentationPage(
            title="Documentation",
            slug="documentation",
            topics=[
                (
                    "documentation_panel",
                    {
                        "title": "Featured Panel",
                        "slug": "featured",
                        "description": "<p>desc</p>",
                        "image": None,
                        "featured_image": True,
                    },
                )
            ],
        )
        self.docs_index.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        self.assertNotContains(response, "faq-card--featured")


class TestAccordionBlock(TestCase):
    def test_accordion_item_block_fields(self):
        block = AccordionItemBlock()
        assert "title" in block.child_blocks
        assert "content" in block.child_blocks

    def test_accordion_block_has_items(self):
        block = AccordionBlock()
        assert "items" in block.child_blocks

    def test_accordion_block_has_color_fields(self):
        block = AccordionBlock()
        assert "header_color" in block.child_blocks
        assert "content_color" in block.child_blocks

    def test_accordion_renders_details_element(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "items": [
                    {"title": "Question 1", "content": "<p>Answer 1</p>"},
                    {"title": "Question 2", "content": "<p>Answer 2</p>"},
                ]
            }
        )
        html = block.render(value)
        assert "<details" in html
        assert "Question 1" in html
        assert "Question 2" in html
        assert "accordion__chevron" in html

    def test_accordion_default_color_no_modifier_classes(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "items": [
                    {"title": "Q", "content": "<p>A</p>"},
                ]
            }
        )
        html = block.render(value)
        assert "accordion--header-" not in html
        assert "accordion--content-" not in html

    def test_accordion_custom_colors_add_modifier_classes(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "header_color": "navy",
                "content_color": "light-grey",
                "items": [
                    {"title": "Q", "content": "<p>A</p>"},
                ],
            }
        )
        html = block.render(value)
        assert "accordion--header-navy" in html
        assert "accordion--content-light-grey" in html

    def test_accordion_renders_layout_wrapper(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "width": "small",
                "alignment": "centre",
                "items": [
                    {"title": "Q1", "content": "<p>A1</p>"},
                ],
            }
        )
        html = block.render(value)
        assert "block-layout--small" in html
        assert "block-layout--align-centre" in html


class TestBackgroundMixin(TestCase):
    def test_background_color_field_exists(self):
        block = BackgroundMixin()
        assert "background_color" in block.child_blocks

    def test_background_color_default(self):
        block = BackgroundMixin()
        assert block.child_blocks["background_color"].meta.default == "default"

    def test_content_block_inherits_background(self):
        block = ContentBlock()
        assert "background_color" in block.child_blocks

    def test_accordion_block_inherits_background(self):
        block = AccordionBlock()
        assert "background_color" in block.child_blocks

    def test_embed_block_inherits_background(self):
        block = MediaEmbedBlock()
        assert "background_color" in block.child_blocks

    def test_image_block_inherits_background(self):
        block = ImageBlock()
        assert "background_color" in block.child_blocks

    def test_column_block_inherits_background(self):
        block = ColumnBlock()
        assert "background_color" in block.child_blocks

    def test_accordion_background_renders_class(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "background_color": "navy",
                "items": [{"title": "Q", "content": "<p>A</p>"}],
            }
        )
        html = block.render(value)
        assert "bg--navy" in html

    def test_accordion_default_background_no_class(self):
        block = AccordionBlock()
        value = block.to_python(
            {
                "items": [{"title": "Q", "content": "<p>A</p>"}],
            }
        )
        html = block.render(value)
        assert "bg--" not in html

    def test_content_block_background_renders_class(self):
        block = ContentBlock()
        value = block.to_python({"background_color": "nceo-purple", "heading": "Test"})
        html = block.render(value)
        assert "bg--nceo-purple" in html

    def test_content_block_default_background_no_class(self):
        block = ContentBlock()
        value = block.to_python({"heading": "Test"})
        html = block.render(value)
        assert "bg--" not in html

    def test_column_background_renders_class(self):
        block = ColumnBlock()
        value = block.to_python(
            {
                "background_color": "steel",
                "content": [{"type": "content_block", "value": {"heading": "Hi"}}],
            }
        )
        html = block.render(value)
        assert "bg--steel" in html

    def test_column_default_background_no_class(self):
        block = ColumnBlock()
        value = block.to_python(
            {
                "content": [{"type": "content_block", "value": {"heading": "Hi"}}],
            }
        )
        html = block.render(value)
        assert "bg--" not in html


class TestLayoutMixin(TestCase):
    def test_layout_fields_exist(self):
        block = LayoutMixin()
        assert "width" in block.child_blocks
        assert "alignment" in block.child_blocks

    def test_layout_defaults(self):
        block = LayoutMixin()
        assert block.child_blocks["width"].meta.default == "default"
        assert block.child_blocks["alignment"].meta.default == "none"
        assert block.child_blocks["vertical_alignment"].meta.default == "top"

    def test_content_block_inherits_layout(self):
        block = ContentBlock()
        assert "width" in block.child_blocks
        assert "alignment" in block.child_blocks
        assert "vertical_alignment" in block.child_blocks

    def test_accordion_block_inherits_layout(self):
        block = AccordionBlock()
        assert "width" in block.child_blocks
        assert "alignment" in block.child_blocks
        assert "vertical_alignment" in block.child_blocks

    def test_content_block_renders_layout_classes(self):
        block = ContentBlock()
        value = block.to_python(
            {
                "width": "medium",
                "alignment": "right",
                "heading": "Test",
            }
        )
        html = block.render(value)
        assert "block-layout--medium" in html
        assert "block-layout--align-right" in html
        assert "block-layout--valign-top" in html

    def test_content_block_renders_vertical_alignment(self):
        block = ContentBlock()
        value = block.to_python(
            {
                "vertical_alignment": "centre",
                "heading": "Test",
            }
        )
        html = block.render(value)
        assert "block-layout--valign-centre" in html


class TestContentBlockImage(TestCase):
    def test_content_block_has_image_link_page_field(self):
        block = ContentBlock()
        assert "image_link_page" in block.child_blocks

    def test_content_block_has_image_link_url_field(self):
        block = ContentBlock()
        assert "image_link_url" in block.child_blocks

    def test_content_block_has_image_width_field(self):
        block = ContentBlock()
        assert "image_width" in block.child_blocks

    def test_content_block_image_width_default(self):
        block = ContentBlock()
        assert block.child_blocks["image_width"].meta.default == "100"

    def test_content_block_has_image_style_field(self):
        block = ContentBlock()
        assert "image_style" in block.child_blocks

    def test_content_block_image_style_default(self):
        block = ContentBlock()
        assert block.child_blocks["image_style"].meta.default == "rounded"

    def test_content_block_has_image_alignment_field(self):
        block = ContentBlock()
        assert "image_alignment" in block.child_blocks

    def test_content_block_image_alignment_default(self):
        block = ContentBlock()
        assert block.child_blocks["image_alignment"].meta.default == "centre"


class TestImageBlock(TestCase):
    def test_image_block_fields(self):
        block = ImageBlock()
        assert "image" in block.child_blocks
        assert "image_link_page" in block.child_blocks
        assert "image_link_url" in block.child_blocks
        assert "image_width" in block.child_blocks
        assert "image_style" in block.child_blocks

    def test_image_block_defaults(self):
        block = ImageBlock()
        assert block.child_blocks["image_width"].meta.default == "100"
        assert block.child_blocks["image_style"].meta.default == "rounded"

    def test_image_block_in_inner_blocks(self):
        block = ColumnBlock()
        inner_types = list(block.child_blocks["content"].child_blocks.keys())
        assert "image" in inner_types


class TestDocumentationPanel(TestCase):
    def test_panel_fields(self):
        block = DocumentationPanel()
        assert "title" in block.child_blocks
        assert "slug" in block.child_blocks
        assert "description" in block.child_blocks
        assert "image" in block.child_blocks
        assert "featured_image" in block.child_blocks

    def test_featured_image_defaults_false(self):
        block = DocumentationPanel()
        assert block.child_blocks["featured_image"].meta.default is False


class TestRowBlock(TestCase):
    def test_row_block_fields(self):
        block = RowBlock()
        assert "layout" in block.child_blocks
        assert "columns" in block.child_blocks

    def test_row_block_renders_grid_classes(self):
        block = RowBlock()
        value = block.to_python(
            {
                "layout": "1-2",
                "columns": [
                    {"content": [{"type": "content_block", "value": {"heading": "Left"}}]},
                    {"content": [{"type": "content_block", "value": {"heading": "Right"}}]},
                ],
            }
        )
        html = block.render(value)
        assert "grid-layout--1-2" in html

    def test_row_block_renders_columns_content(self):
        block = RowBlock()
        value = block.to_python(
            {
                "layout": "1-1",
                "columns": [
                    {"content": [{"type": "content_block", "value": {"heading": "Left Col"}}]},
                    {"content": [{"type": "content_block", "value": {"heading": "Right Col"}}]},
                ],
            }
        )
        html = block.render(value)
        assert "Left Col" in html
        assert "Right Col" in html
        assert html.count("grid-layout__column") == 2

    def test_row_block_gap_default(self):
        block = RowBlock()
        value = block.to_python(
            {
                "layout": "2-1",
                "columns": [
                    {"content": []},
                ],
            }
        )
        html = block.render(value)
        assert "grid-layout--2-1" in html


class TestColumnBlock(TestCase):
    def test_column_block_has_content_stream(self):
        block = ColumnBlock()
        assert "content" in block.child_blocks

    def test_column_block_has_stretch_field(self):
        block = ColumnBlock()
        assert "stretch" in block.child_blocks

    def test_column_cannot_contain_rows(self):
        """Columns should not allow nested row blocks (prevents infinite nesting)."""
        block = ColumnBlock()
        inner_types = list(block.child_blocks["content"].child_blocks.keys())
        assert "columns" not in inner_types

    def test_column_renders_stretch_class_when_enabled(self):
        block = ColumnBlock()
        value = block.to_python(
            {
                "stretch": True,
                "content": [{"type": "content_block", "value": {"heading": "Hello"}}],
            }
        )
        html = block.render(value)
        assert "column-block--stretch" in html

    def test_column_no_stretch_class_when_disabled(self):
        block = ColumnBlock()
        value = block.to_python(
            {
                "stretch": False,
                "content": [{"type": "content_block", "value": {"heading": "Hello"}}],
            }
        )
        html = block.render(value)
        assert "column-block--stretch" not in html


class TestMediaEmbedBlock(TestCase):
    def test_embed_block_fields(self):
        block = MediaEmbedBlock()
        assert "url" in block.child_blocks
        assert "caption" in block.child_blocks

    def test_embed_block_inherits_layout(self):
        block = MediaEmbedBlock()
        assert "width" in block.child_blocks
        assert "alignment" in block.child_blocks

    def test_embed_in_inner_blocks(self):
        block_types = [name for name, _ in _inner_blocks()]
        assert "embed" in block_types

    def test_embed_in_body_blocks(self):
        block_types = [name for name, _ in _body_blocks()]
        assert "embed" in block_types


class TestBodyBlockHelpers(TestCase):
    def test_body_blocks_includes_columns(self):
        block_types = [name for name, _ in _body_blocks()]
        assert "columns" in block_types

    def test_inner_blocks_excludes_columns(self):
        block_types = [name for name, _ in _inner_blocks()]
        assert "columns" not in block_types

    def test_inner_blocks_includes_cta(self):
        block_types = [name for name, _ in _inner_blocks()]
        assert "cta" in block_types

    def test_body_blocks_includes_cta(self):
        block_types = [name for name, _ in _body_blocks()]
        assert "cta" in block_types


class TestCTABlock(TestCase):
    def test_cta_block_fields(self):
        block = CTABlock()
        assert "text" in block.child_blocks
        assert "link_page" in block.child_blocks
        assert "link_url" in block.child_blocks
        assert "button_style" in block.child_blocks

    def test_cta_block_inherits_layout(self):
        block = CTABlock()
        assert "width" in block.child_blocks
        assert "alignment" in block.child_blocks
        assert "vertical_alignment" in block.child_blocks

    def test_cta_block_inherits_background(self):
        block = CTABlock()
        assert "background_color" in block.child_blocks
        assert "full_width_background" in block.child_blocks

    def test_cta_button_style_default(self):
        block = CTABlock()
        assert block.child_blocks["button_style"].meta.default == "primary"

    def test_cta_renders_url_link(self):
        block = CTABlock()
        value = block.to_python(
            {
                "text": "Sign Up",
                "link_url": "https://example.com/signup",
            }
        )
        html = block.render(value)
        assert "Sign Up" in html
        assert 'href="https://example.com/signup"' in html
        assert "primary-button" in html

    def test_cta_secondary_style(self):
        block = CTABlock()
        value = block.to_python(
            {
                "text": "Learn More",
                "link_url": "https://example.com",
                "button_style": "secondary",
            }
        )
        html = block.render(value)
        assert "secondary-button" in html

    def test_cta_no_link_renders_nothing(self):
        block = CTABlock()
        value = block.to_python({"text": "Orphan"})
        html = block.render(value)
        assert "<a" not in html


class TestLabel(TestCase):
    def test_slug_auto_filled(self):
        label = Label(name="Getting Started", color="nceo-purple")
        label.save()
        assert label.slug == "getting-started"

    def test_slug_deduplicated_on_collision(self):
        Label.objects.create(name="Getting Started", color="navy")
        label2 = Label(name="Getting Started!", color="steel")
        label2.save()
        assert label2.slug == "getting-started-1"

    def test_slug_fallback_when_name_slugifies_to_empty(self):
        label = Label(name="🎉🎉", color="nceo-purple")
        label.save()
        assert label.slug.startswith("label")

    def test_slug_truncated_when_suffixed_exceeds_max_length(self):
        long_name = "a" * 50
        Label.objects.create(name=long_name, color="navy")
        label2 = Label(name=long_name + "!", color="steel")
        label2.save()
        assert len(label2.slug) <= 50

    def test_slug_not_overwritten_on_rename(self):
        label = Label(name="Getting Started", color="nceo-purple")
        label.save()
        original_slug = label.slug
        label.name = "Getting Started Guide"
        label.save()
        assert label.slug == original_slug

    def test_unique_name(self):
        Label.objects.create(name="Unique", color="navy")
        with pytest.raises(IntegrityError):
            Label.objects.create(name="Unique", color="steel")

    def test_str_returns_name(self):
        label = Label(name="API Docs", color="blue")
        label.save()
        assert str(label) == "API Docs"

    def test_ordering_by_name(self):
        Label.objects.create(name="Charlie", color="navy")
        Label.objects.create(name="Alpha", color="steel")
        Label.objects.create(name="Bravo", color="blue")
        names = list(Label.objects.values_list("name", flat=True))
        assert names == ["Alpha", "Bravo", "Charlie"]

    @patch("home.models.clear_cache")
    def test_save_purges_cache(self, mock_clear):
        label = Label(name="Cache Test", color="navy")
        label.save()
        mock_clear.assert_called_once()

    @patch("home.models.clear_cache")
    def test_delete_purges_cache(self, mock_clear):
        label = Label(name="Cache Test", color="navy")
        label.save()
        mock_clear.reset_mock()
        label.delete()
        mock_clear.assert_called_once()


class TestDocumentationPanelLabels(TestCase):
    def test_panel_has_labels_field(self):
        block = DocumentationPanel()
        assert "labels" in block.child_blocks

    def test_labels_not_required(self):
        block = DocumentationPanel()
        assert block.child_blocks["labels"].meta.required is False


class TestNotificationBannerModel(TestCase):
    def test_permanent_banner_is_active(self):
        banner = NotificationBanner(message="<p>Always on</p>", is_enabled=True)
        banner.save()
        assert banner.is_active() is True

    def test_disabled_banner_is_inactive(self):
        banner = NotificationBanner(message="<p>Off</p>", is_enabled=False)
        banner.save()
        assert banner.is_active() is False

    def test_future_banner_is_inactive(self):
        future = timezone.now() + timedelta(hours=1)
        banner = NotificationBanner(message="<p>Future</p>", is_enabled=True, starts_at=future)
        banner.save()
        assert banner.is_active() is False

    def test_expired_banner_is_inactive(self):
        past = timezone.now() - timedelta(hours=1)
        banner = NotificationBanner(message="<p>Expired</p>", is_enabled=True, ends_at=past)
        banner.save()
        assert banner.is_active() is False

    def test_current_window_banner_is_active(self):
        now = timezone.now()
        banner = NotificationBanner(
            message="<p>Current</p>",
            is_enabled=True,
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(hours=1),
        )
        banner.save()
        assert banner.is_active() is True

    def test_active_queryset_excludes_inactive(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Active</p>", is_enabled=True)
        NotificationBanner.objects.create(message="<p>Disabled</p>", is_enabled=False)
        NotificationBanner.objects.create(message="<p>Future</p>", is_enabled=True, starts_at=now + timedelta(hours=1))
        NotificationBanner.objects.create(message="<p>Expired</p>", is_enabled=True, ends_at=now - timedelta(hours=1))
        active = list(NotificationBanner.objects.active(now))
        assert len(active) == 1
        assert active[0].message == "<p>Active</p>"

    def test_active_queryset_orders_by_priority(self):
        NotificationBanner.objects.create(message="<p>Low</p>", is_enabled=True, priority=1)
        NotificationBanner.objects.create(message="<p>High</p>", is_enabled=True, priority=10)
        active = list(NotificationBanner.objects.active())
        assert active[0].message == "<p>High</p>"
        assert active[1].message == "<p>Low</p>"

    def test_clean_rejects_both_link_page_and_url(self):
        banner = NotificationBanner(
            message="<p>Test</p>",
            link_page_id=1,
            link_url="https://example.com",
        )
        with pytest.raises(ValidationError) as exc_info:
            banner.clean()
        assert "link_page" in exc_info.value.message_dict
        assert "link_url" in exc_info.value.message_dict

    def test_clean_rejects_invalid_date_range(self):
        now = timezone.now()
        banner = NotificationBanner(
            message="<p>Test</p>",
            starts_at=now,
            ends_at=now - timedelta(hours=1),
        )
        with pytest.raises(ValidationError) as exc_info:
            banner.clean()
        assert "ends_at" in exc_info.value.message_dict

    def test_str_returns_title_when_present(self):
        banner = NotificationBanner(title="Maintenance", message="<p>Test</p>")
        banner.save()
        assert str(banner) == "Maintenance"

    def test_str_returns_fallback_when_title_blank(self):
        banner = NotificationBanner(message="<p>Test</p>")
        banner.save()
        assert str(banner) == f"Banner {banner.pk}"

    @patch("home.models.clear_cache")
    def test_save_purges_cache(self, mock_clear):
        banner = NotificationBanner(message="<p>Test</p>")
        banner.save()
        mock_clear.assert_called_once()

    @patch("home.models.clear_cache")
    def test_delete_purges_cache(self, mock_clear):
        banner = NotificationBanner(message="<p>Test</p>")
        banner.save()
        mock_clear.reset_mock()
        banner.delete()
        mock_clear.assert_called_once()


@override_settings(WAGTAIL_CACHE=False)
class TestNotificationBannerRendering(LandingPageTestMixin, TestCase):
    def test_no_inactive_banner_renders(self):
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertNotContains(response, "notification-banner")

    def test_active_banner_renders_on_page(self):
        NotificationBanner.objects.create(
            title="Heads up",
            message="<p>System update today</p>",
            status="info",
            is_enabled=True,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, "notification-banner")
        self.assertContains(response, "Heads up")
        self.assertContains(response, "System update today")

    def test_highest_priority_wins(self):
        NotificationBanner.objects.create(
            title="Low",
            message="<p>Low priority</p>",
            is_enabled=True,
            priority=1,
        )
        NotificationBanner.objects.create(
            title="High",
            message="<p>High priority</p>",
            is_enabled=True,
            priority=10,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, "High priority")
        self.assertNotContains(response, "Low priority")

    def test_internal_cta_link_renders(self):
        target = GenericPage(title="Target", slug="target")
        self.home.add_child(instance=target)
        NotificationBanner.objects.create(
            message="<p>Click here</p>",
            is_enabled=True,
            link_text="Go",
            link_page=target,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, f'href="{target.url}"')
        self.assertContains(response, "Go")

    def test_external_cta_link_renders(self):
        NotificationBanner.objects.create(
            message="<p>Click here</p>",
            is_enabled=True,
            link_text="External",
            link_url="https://example.com",
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, 'href="https://example.com"')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, "External")

    def test_critical_banner_has_alert_role(self):
        NotificationBanner.objects.create(
            message="<p>Critical</p>",
            status="critical",
            is_enabled=True,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, 'role="alert"')

    def test_non_critical_banner_has_status_role(self):
        NotificationBanner.objects.create(
            message="<p>Info</p>",
            status="info",
            is_enabled=True,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, 'role="status"')
        self.assertNotContains(response, 'role="alert"')

    def test_banner_renders_dismiss_button(self):
        banner = NotificationBanner.objects.create(
            message="<p>Dismiss me</p>",
            status="info",
            is_enabled=True,
        )
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, "notification-banner__dismiss")
        self.assertContains(response, 'aria-label="Dismiss notification"')
        self.assertContains(
            response,
            f'data-dismiss-key="banner-{banner.id}-',
        )


class TestNotificationBannerGetActiveBanner(TestCase):
    def test_get_active_banner_returns_none_when_empty(self):
        assert NotificationBanner.get_active_banner() is None

    def test_get_active_banner_returns_past_start_banner(self):
        now = timezone.now()
        banner = NotificationBanner.objects.create(
            message="<p>Test</p>",
            is_enabled=True,
            starts_at=now - timedelta(minutes=5),
        )
        assert NotificationBanner.get_active_banner() == banner

    def test_get_active_banner_prefers_higher_priority(self):
        NotificationBanner.objects.create(message="<p>Low</p>", is_enabled=True, priority=1)
        high = NotificationBanner.objects.create(message="<p>High</p>", is_enabled=True, priority=10)
        assert NotificationBanner.get_active_banner() == high


class TestNotificationBannerBoundary(TestCase):
    def test_next_boundary_from_starts_at(self):
        now = timezone.now()
        future = now + timedelta(minutes=10)
        NotificationBanner.objects.create(message="<p>Upcoming</p>", is_enabled=True, starts_at=future)
        assert NotificationBanner.get_next_boundary(now) == future

    def test_next_boundary_from_ends_at(self):
        now = timezone.now()
        end = now + timedelta(minutes=5)
        NotificationBanner.objects.create(
            message="<p>Current</p>", is_enabled=True, starts_at=now - timedelta(minutes=1), ends_at=end
        )
        assert NotificationBanner.get_next_boundary(now) == end

    def test_next_boundary_picks_nearest(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Far</p>", is_enabled=True, starts_at=now + timedelta(minutes=20))
        near = now + timedelta(minutes=3)
        NotificationBanner.objects.create(
            message="<p>Near</p>", is_enabled=True, starts_at=now - timedelta(minutes=1), ends_at=near
        )
        assert NotificationBanner.get_next_boundary(now) == near

    def test_no_boundary_when_no_time_bound_banners(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Permanent</p>", is_enabled=True)
        assert NotificationBanner.get_next_boundary(now) is None

    def test_no_boundary_when_only_disabled_time_bound_banners(self):
        now = timezone.now()
        NotificationBanner.objects.create(
            message="<p>Disabled</p>", is_enabled=False, starts_at=now + timedelta(minutes=5)
        )
        assert NotificationBanner.get_next_boundary(now) is None


class TestBannerCacheMiddleware(TestCase):
    def _make_middleware(self, response):
        return BannerCacheMiddleware(lambda req: response)

    def test_skips_non_html_responses(self):
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("{}", status=200, content_type="application/json")
        result = self._make_middleware(response)(request)
        assert "Cache-Control" not in result

    def test_skips_non_html_404(self):
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("not found", status=404, content_type="application/json")
        result = self._make_middleware(response)(request)
        assert "Cache-Control" not in result

    def test_sets_no_cache_on_404_html_when_boundary_near(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=2))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html>not found</html>", status=404, content_type="text/html")
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}}
        ):
            result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-cache"

    def test_skips_when_boundary_beyond_timeout(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=10))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}}
        ):
            result = self._make_middleware(response)(request)
        assert "Cache-Control" not in result

    def test_sets_no_cache_when_boundary_within_timeout(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=2))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}}
        ):
            result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-cache"

    def test_sets_no_cache_when_timeout_is_none(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(hours=1))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": None}}
        ):
            result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-cache"

    def test_overrides_existing_cache_control_when_boundary_near(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=1))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        response["Cache-Control"] = "max-age=60"
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}}
        ):
            result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-cache"

    def test_leaves_existing_cache_control_when_boundary_beyond_timeout(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=10))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        response["Cache-Control"] = "max-age=60"
        with override_settings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}}
        ):
            result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "max-age=60"

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}})
    def test_preserves_private_when_boundary_near(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=1))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        response["Cache-Control"] = "private, max-age=60"
        result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "private, max-age=60"

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}})
    def test_preserves_no_store_when_boundary_near(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=1))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        response["Cache-Control"] = "no-store, max-age=60"
        result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-store, max-age=60"

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache", "TIMEOUT": 300}})
    def test_preserves_no_cache_when_boundary_near(self):
        now = timezone.now()
        NotificationBanner.objects.create(message="<p>Test</p>", is_enabled=True, ends_at=now + timedelta(minutes=1))
        request = type("R", (), {"path": "/"})()
        response = HttpResponse("<html></html>", status=200, content_type="text/html")
        response["Cache-Control"] = "no-cache, max-age=60"
        result = self._make_middleware(response)(request)
        assert result.get("Cache-Control") == "no-cache, max-age=60"
