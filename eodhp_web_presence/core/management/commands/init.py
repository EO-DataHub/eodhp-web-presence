from dataclasses import dataclass, field
from typing import Type

from django.core.management.base import BaseCommand
from home import models
from wagtail.models import Page, Site


@dataclass(frozen=True)
class PageData:
    title: str
    type: Type[Page]
    children: list[str, "PageData"] = field(default_factory=list)


class Command(BaseCommand):
    help = "Create an initial web presence"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating initial web presence...")
        root = Page.objects.get(title="Root")
        site = Site.objects.get(is_default_site=True)

        pages = [
            PageData(
                title="Home",
                type=models.HomePage,
                children=[
                    PageData(title="About", type=models.AboutPage),
                    PageData(title="Contact", type=models.ContactPage),
                    PageData(title="Support", type=models.SupportIndexPage),
                    PageData(
                        title="News",
                        type=models.NewsPage,
                        children=[
                            PageData(title="Article 1", type=models.NewsArticlePage),
                            PageData(title="Article 2", type=models.NewsArticlePage),
                            PageData(title="Article 3", type=models.NewsArticlePage),
                        ],
                    ),
                ],
            ),
        ]

        for ii, page_data in enumerate(pages):
            page = self.create_page(root, page_data)

            if ii == 0:
                site.root_page = page
                site.save()
                self.stdout.write(self.style.SUCCESS(f"{page.title} set as root page"))

    def create_page(self, parent: Page | None, page_data: PageData) -> Page:
        try:
            page = page_data.type.objects.get(title=page_data.title).specific
        except page_data.type.DoesNotExist:
            page = page_data.type(title=page_data.title)
            parent.add_child(instance=page)
            page.save()
            self.stdout.write(self.style.SUCCESS(f"{page.title} page created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"{page.title} already exists"))

        if page_data.children:
            for child_data in page_data.children:
                self.create_page(page, child_data)

        return page
