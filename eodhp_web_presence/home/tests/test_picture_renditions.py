from django.test import TestCase, override_settings
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file_jpeg
from wagtail.models import Page, Site

from home.blocks import ContentBlock, ImageBlock
from home.models import (
    AboutIndexPage,
    DocsIndexPage,
    DocumentationPage,
    GenericPage,
    HomePage,
)

WagtailImage = get_image_model()


class LandingPageTestMixin:
    def setUp(self):
        super().setUp()
        self.root = Page.objects.get(depth=1)
        self.home = HomePage(title="Test Home", slug="testhome")
        self.root.add_child(instance=self.home)
        Site.objects.update_or_create(
            is_default_site=True,
            defaults={"root_page": self.home, "hostname": "localhost"},
        )


def _create_image() -> WagtailImage:
    image = WagtailImage.objects.create(
        title="Test image",
        file=get_test_image_file_jpeg(),
    )
    return image


@override_settings(WAGTAIL_CACHE=False)
class TestHeroPictureTag(LandingPageTestMixin, TestCase):
    def test_landing_page_hero_uses_picture_tag(self):
        img = _create_image()
        page = AboutIndexPage(title="About", slug="about", hero_image=img)
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "<picture>" in content
        assert 'type="image/avif"' in content
        assert 'type="image/webp"' in content
        assert ".jpg" in content

    def test_landing_page_hero_no_background_image_style(self):
        img = _create_image()
        page = AboutIndexPage(title="About", slug="about2", hero_image=img)
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        content = response.content.decode()
        assert "background-image" not in content

    def test_generic_page_hero_uses_picture_tag(self):
        img = _create_image()
        page = GenericPage(title="Hero Page", slug="hero-page", hero_image=img)
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "<picture>" in content
        assert 'type="image/avif"' in content
        assert 'type="image/webp"' in content
        assert ".jpg" in content
        assert "background-image" not in content


@override_settings(WAGTAIL_CACHE=False)
class TestImageBlockPictureTag(TestCase):
    def test_image_block_renders_picture(self):
        block = ImageBlock()
        img = _create_image()
        value = block.to_python({"image": img.pk})
        html = block.render(value)

        assert "<picture>" in html
        assert 'type="image/avif"' in html
        assert 'type="image/webp"' in html
        assert ".jpg" in html

    def test_image_block_no_original_src(self):
        block = ImageBlock()
        img = _create_image()
        value = block.to_python({"image": img.pk})
        html = block.render(value)

        assert "original" not in html


@override_settings(WAGTAIL_CACHE=False)
class TestContentBlockPictureTag(TestCase):
    def test_content_block_image_renders_picture(self):
        block = ContentBlock()
        img = _create_image()
        value = block.to_python({"image": img.pk, "heading": "Test"})
        html = block.render(value)

        assert "<picture>" in html
        assert 'type="image/avif"' in html
        assert 'type="image/webp"' in html
        assert ".jpg" in html

    def test_content_block_no_original_src(self):
        block = ContentBlock()
        img = _create_image()
        value = block.to_python({"image": img.pk, "heading": "Test"})
        html = block.render(value)

        assert "original" not in html


@override_settings(WAGTAIL_CACHE=False)
class TestTopicsGridPictureTag(LandingPageTestMixin, TestCase):
    def test_featured_card_uses_picture_tag(self):
        img = _create_image()
        page = GenericPage(
            title="Topics Page",
            slug="topics-picture",
            body=[
                (
                    "topics_grid",
                    {
                        "background_color": "default",
                        "full_width_background": False,
                        "topics": [
                            {
                                "title": "Featured Topic",
                                "slug": "featured-topic",
                                "description": "<p>A featured topic</p>",
                                "image": img,
                                "featured_image": True,
                            }
                        ],
                    },
                )
            ],
        )
        self.home.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "<picture>" in content
        assert 'type="image/avif"' in content
        assert 'type="image/webp"' in content
        assert ".jpg" in content
        assert "background-image" not in content

    def test_thumbnail_card_uses_picture_tag(self):
        img = _create_image()
        page = GenericPage(
            title="Thumb Page",
            slug="thumb-picture",
            body=[
                (
                    "topics_grid",
                    {
                        "background_color": "default",
                        "full_width_background": False,
                        "topics": [
                            {
                                "title": "Thumb Topic",
                                "slug": "thumb-topic",
                                "description": "<p>Topic with thumb</p>",
                                "image": img,
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
        content = response.content.decode()
        assert "<picture>" in content
        assert 'type="image/avif"' in content
        assert 'type="image/webp"' in content


@override_settings(WAGTAIL_CACHE=False)
class TestDocumentationPagePictureTag(LandingPageTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.docs_index = DocsIndexPage(title="Docs", slug="docs")
        self.home.add_child(instance=self.docs_index)

    def test_documentation_featured_card_uses_picture(self):
        img = _create_image()
        page = DocumentationPage(
            title="Doc Page",
            slug="doc-page",
            topics=[
                (
                    "documentation_panel",
                    {
                        "title": "Featured Doc",
                        "slug": "featured-doc",
                        "description": "<p>desc</p>",
                        "image": img,
                        "featured_image": True,
                    },
                )
            ],
        )
        self.docs_index.add_child(instance=page)

        response = self.client.get(page.url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "<picture>" in content
        assert 'type="image/avif"' in content
        assert 'type="image/webp"' in content
        assert "background-image" not in content
