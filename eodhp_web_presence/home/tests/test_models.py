from django.test import TestCase, override_settings
from wagtail.models import Page, Site

from home.models import (
    AboutIndexPage,
    AccordionBlock,
    AccordionItemBlock,
    BackgroundMixin,
    CaseStudiesPage,
    CatalogueIndexPage,
    ColumnBlock,
    ContentBlock,
    DataIndexPage,
    DocsIndexPage,
    DocumentationPage,
    DocumentationPanel,
    GenericPage,
    HomePage,
    ImageBlock,
    LayoutMixin,
    MediaEmbedBlock,
    RowBlock,
    _body_blocks,
    _inner_blocks,
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


@override_settings(WAGTAIL_CACHE=False)
class TestGenericPage(LandingPageTestMixin, TestCase):
    def test_generic_page_serves(self):
        page = GenericPage(title="Test Page", slug="test-page")
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200

    def test_generic_page_with_topics(self):
        page = GenericPage(
            title="Topics Page",
            slug="topics-page",
            topics=[
                (
                    "topic_panel",
                    {
                        "title": "My Topic",
                        "slug": "my-topic",
                        "description": "<p>A description</p>",
                        "image": None,
                        "featured_image": False,
                    },
                )
            ],
        )
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        self.assertContains(response, "My Topic")
        self.assertTemplateUsed(response, "home/includes/topic_card.html")


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
