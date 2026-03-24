from django.test import TestCase, override_settings
from wagtail.models import Page, Site

from home.models import (
    AboutIndexPage,
    AccordionBlock,
    AccordionItemBlock,
    CaseStudiesPage,
    CatalogueIndexPage,
    DataIndexPage,
    DocsIndexPage,
    DocumentationPage,
    DocumentationPanel,
    GenericPage,
    HomePage,
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
