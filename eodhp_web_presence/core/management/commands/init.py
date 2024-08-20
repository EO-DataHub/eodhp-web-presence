from dataclasses import dataclass, field
from random import randrange
from typing import Type

from django.core.management.base import BaseCommand
from home import models
from wagtail.models import Page, Site
from wagtail.rich_text import RichText


@dataclass(frozen=True)
class PageData:
    title: str
    type: Type[Page]
    body: str = ""
    children: list[str, "PageData"] = field(default_factory=list)
    published: bool = True


def generate_page(title, type):
    body = ""
    for _ in range(randrange(1, 5)):  # paragraphs
        for _ in range(randrange(1, 50)):  # sentences
            body += title.title() + " " + (f"{title.lower()} " * randrange(1, 20)).rstrip() + ". "
        body += "\n\n"

    return PageData(title=title, type=type, body=RichText(body))


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
                body=(generate_page(title="Home", type=None)).body,
                children=[
                    generate_page(title="About", type=models.AboutPage),
                    generate_page(title="Contact", type=models.ContactPage),
                    PageData(
                        title="Support",
                        type=models.SupportIndexPage,
                        children=[
                            PageData(title="Accounts", type=models.SupportAreaPage),
                            PageData(title="JupyterHub", type=models.SupportAreaPage),
                            PageData(title="Projects", type=models.SupportAreaPage),
                            PageData(title="Workflows", type=models.SupportAreaPage),
                            PageData(title="Catalogue", type=models.SupportAreaPage),
                            PageData(title="Data Services", type=models.SupportAreaPage),
                            PageData(
                                title="Area A",
                                type=models.SupportAreaPage,
                                children=[
                                    generate_page(title="Aardvark", type=models.SupportTopicPage),
                                    generate_page(title="Aeroplane", type=models.SupportTopicPage),
                                    generate_page(title="Alligator", type=models.SupportTopicPage),
                                    generate_page(title="Anchor", type=models.SupportTopicPage),
                                    generate_page(title="Apple", type=models.SupportTopicPage),
                                    generate_page(title="Astronaut", type=models.SupportTopicPage),
                                    PageData(title="Aardvark?", type=models.SupportFAQPage),
                                    PageData(title="Aeroplane?", type=models.SupportFAQPage),
                                    PageData(title="Alligator?", type=models.SupportFAQPage),
                                    PageData(title="Anchor?", type=models.SupportFAQPage),
                                    PageData(title="Apple?", type=models.SupportFAQPage),
                                    PageData(title="Astronaut?", type=models.SupportFAQPage),
                                ],
                            ),
                            PageData(
                                title="Area B",
                                type=models.SupportAreaPage,
                                children=[
                                    generate_page(title="Ball", type=models.SupportTopicPage),
                                    generate_page(title="Banana", type=models.SupportTopicPage),
                                    generate_page(title="Bear", type=models.SupportTopicPage),
                                    generate_page(title="Book", type=models.SupportTopicPage),
                                    generate_page(title="Bus", type=models.SupportTopicPage),
                                ],
                            ),
                            PageData(
                                title="Area C",
                                type=models.SupportAreaPage,
                                children=[
                                    generate_page(title="Cat", type=models.SupportTopicPage),
                                    generate_page(title="Cake", type=models.SupportTopicPage),
                                    generate_page(title="Car", type=models.SupportTopicPage),
                                    generate_page(title="Cave", type=models.SupportTopicPage),
                                    generate_page(title="Carrot", type=models.SupportTopicPage),
                                    generate_page(title="Chicken", type=models.SupportTopicPage),
                                    generate_page(title="Cow", type=models.SupportTopicPage),
                                ],
                            ),
                        ],
                    ),
                    PageData(
                        title="News",
                        type=models.NewsPage,
                        children=[
                            generate_page(title="Article 1", type=models.NewsArticlePage),
                            generate_page(title="Article 2", type=models.NewsArticlePage),
                            generate_page(title="Article 3", type=models.NewsArticlePage),
                            generate_page(title="Article 4", type=models.NewsArticlePage),
                            generate_page(title="Article 5", type=models.NewsArticlePage),
                            generate_page(title="Article 6", type=models.NewsArticlePage),
                            generate_page(title="Article 7", type=models.NewsArticlePage),
                            generate_page(title="Article 8", type=models.NewsArticlePage),
                            generate_page(title="Article 9", type=models.NewsArticlePage),
                            generate_page(title="Article 10", type=models.NewsArticlePage),
                        ],
                    ),
                ],
            ),
        ]

        for ii, page_data in enumerate(pages):
            page = self.create_page(root, page_data, ii)

            if ii == 0:
                site.root_page = page
                site.save()
                self.stdout.write(self.style.SUCCESS(f"{page.title} set as root page"))

    def create_page(self, parent: Page | None, page_data: PageData, value: int = None) -> Page:
        try:
            page = page_data.type.objects.get(title=page_data.title).specific
        except page_data.type.DoesNotExist:
            try:
                page = page_data.type(title=page_data.title, body=page_data.body)
            except TypeError:  # not all templates have body text
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
