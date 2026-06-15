import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file

from home.models import (
    CaseStudiesPage,
    FeaturedCaseStudy,
    GenericPage,
    HeroCarouselImage,
    Label,
)

from .test_models import LandingPageTestMixin


class TestHome(TestCase):
    def test_status_code__success(self):
        home_page_get = self.client.get("/")
        assert home_page_get.status_code == 200


class FeaturedCaseStudiesTestMixin(LandingPageTestMixin):
    """Home page plus a Case Studies section with featured entries."""

    def setUp(self):
        super().setUp()
        self.case_studies_index = CaseStudiesPage(title="Case Studies", slug="case-studies")
        self.home.add_child(instance=self.case_studies_index)

        self.case_study_1 = GenericPage(
            title="AI-Driven Shoreline Extraction",
            slug="shoreline",
            intro="<p>Neural networks mapping land-water boundaries.</p>",
        )
        self.case_studies_index.add_child(instance=self.case_study_1)

        self.case_study_2 = GenericPage(title="Rapid Tree Canopy Detection", slug="canopy")
        self.case_studies_index.add_child(instance=self.case_study_2)

        self.label = Label.objects.create(name="Government", color="navy")
        for sort_order, page in enumerate([self.case_study_1, self.case_study_2]):
            FeaturedCaseStudy.objects.create(
                page=self.home,
                case_study=page.page_ptr,
                label=self.label,
                sort_order=sort_order,
            )


@override_settings(WAGTAIL_CACHE=False)
class TestHomePage(FeaturedCaseStudiesTestMixin, TestCase):
    def test_homepage_serves_redesign(self):
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertTemplateUsed(response, "home/home_page.html")
        self.assertContains(response, "overview-band")
        self.assertContains(response, "platform-tile")

    def test_design_param_is_ignored(self):
        response = self.client.get(self.home.url, {"design": "2"})
        assert response.status_code == 200
        self.assertTemplateUsed(response, "home/home_page.html")

    def test_carousel_renders_featured_case_studies(self):
        response = self.client.get(self.home.url)
        self.assertContains(response, "case-carousel")
        self.assertContains(response, self.case_study_1.title)
        self.assertContains(response, self.case_study_2.title)
        self.assertContains(response, "case-carousel__badge--navy")

    def test_platform_tiles_render_aims(self):
        target = GenericPage(title="Tile Target", slug="tile-target")
        self.home.add_child(instance=target)
        self.home.aim_1_title = "Data Catalogue"
        self.home.aim_1_description = "<p>A searchable catalogue of datasets.</p>"
        self.home.aim_1_page = target
        self.home.save()

        response = self.client.get(self.home.url)
        self.assertContains(response, "Data Catalogue")
        self.assertContains(response, "A searchable catalogue of datasets.")
        self.assertContains(response, f'href="{target.url}"')
        self.assertContains(response, "Find out more")

    def test_audience_section_renders(self):
        response = self.client.get(self.home.url)
        self.assertContains(response, "Who is the Earth Observation DataHub for?")
        self.assertContains(response, 'class="audience-card"', count=3)
        self.assertContains(response, "Government and Public Sector")
        self.assertContains(response, "Industry &amp; Commercial Operators")
        self.assertContains(response, "Academia &amp; Researchers")

    def test_platform_tile_renders_image_when_set(self):
        self.home.aim_1_image.save("aim1.png", get_test_image_file(), save=True)

        response = self.client.get(self.home.url)
        self.assertContains(response, "platform-tile__image", count=1)
        # Tiles without an image simply show title and description.
        self.assertContains(response, 'class="platform-tile"', count=4)

    def test_platform_skips_empty_aim_slots(self):
        self.home.aim_4_title = ""
        self.home.save()

        response = self.client.get(self.home.url)
        self.assertContains(response, 'class="platform-tile"', count=3)


@override_settings(WAGTAIL_CACHE=False)
class TestHeroCarousel(FeaturedCaseStudiesTestMixin, TestCase):
    def test_hero_carousel_renders_picked_imagery(self):
        for i in range(2):
            image = Image.objects.create(title=f"Hero {i}", file=get_test_image_file())
            HeroCarouselImage.objects.create(
                page=self.home,
                image=image,
                caption=f"Caption {i}",
                sort_order=i,
            )

        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertContains(response, "data-hero-carousel")
        self.assertContains(response, "hero-carousel__bg", count=2)
        self.assertContains(response, "Caption 0")
        # The live-site hero text stays on top of the imagery.
        self.assertContains(response, "We provide a single point of access to")

    def test_hero_falls_back_to_static_image_without_picks(self):
        response = self.client.get(self.home.url)
        assert response.status_code == 200
        self.assertNotContains(response, "data-hero-carousel")
        self.assertContains(response, 'class="hero"')
        self.assertContains(response, "We provide a single point of access to")


@override_settings(WAGTAIL_CACHE=False)
class TestFeaturedCaseStudy(FeaturedCaseStudiesTestMixin, TestCase):
    def test_display_summary_falls_back_to_intro(self):
        featured = self.home.featured_case_studies.first()
        assert "Neural networks mapping land-water boundaries." in featured.display_summary
        assert "<p>" not in featured.display_summary

    def test_display_summary_prefers_override(self):
        featured = self.home.featured_case_studies.first()
        featured.summary_override = "Override summary."
        assert featured.display_summary == "Override summary."

    def test_display_image_falls_back_to_hero_image(self):
        hero = Image.objects.create(title="Hero", file=get_test_image_file())
        self.case_study_1.hero_image = hero
        self.case_study_1.save()

        featured = self.home.featured_case_studies.first()
        assert featured.display_image == hero

    def test_display_image_prefers_override(self):
        hero = Image.objects.create(title="Hero", file=get_test_image_file())
        override = Image.objects.create(title="Override", file=get_test_image_file())
        self.case_study_1.hero_image = hero
        self.case_study_1.save()

        featured = self.home.featured_case_studies.first()
        featured.image_override = override
        assert featured.display_image == override

    def test_display_image_none_without_images(self):
        featured = self.home.featured_case_studies.first()
        assert featured.display_image is None

    def test_clean_rejects_pages_outside_case_studies_section(self):
        outside = GenericPage(title="Outside", slug="outside")
        self.home.add_child(instance=outside)

        featured = FeaturedCaseStudy(page=self.home, case_study=outside.page_ptr)
        with pytest.raises(ValidationError):
            featured.clean()

    def test_clean_accepts_case_study_pages(self):
        featured = self.home.featured_case_studies.first()
        featured.clean()

    def test_clean_accepts_pages_under_legacy_generic_case_studies_section(self):
        legacy_home = self.home.__class__(title="Legacy Home", slug="legacy-home")
        self.root.add_child(instance=legacy_home)
        legacy_case_studies_index = GenericPage(title="Case Studies", slug="case-studies")
        legacy_home.add_child(instance=legacy_case_studies_index)
        legacy_case_study = GenericPage(title="Legacy case study", slug="legacy-case-study")
        legacy_case_studies_index.add_child(instance=legacy_case_study)

        featured = FeaturedCaseStudy(page=legacy_home, case_study=legacy_case_study.page_ptr)
        featured.clean()
