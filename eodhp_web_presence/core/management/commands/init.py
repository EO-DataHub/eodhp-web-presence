import copy
import datetime
import os
from io import BytesIO
from random import randint, randrange

import pytz
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from gibberish import Gibberish
from home import models
from PIL import Image, ImageDraw
from wagtail.images.models import Image as WagtailImage
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

gib = Gibberish()


class PageData:
    def __init__(self, **kwargs):
        self.children = None
        self.type = None
        self.__dict__.update(kwargs)


def generate_date() -> datetime:
    period = datetime.datetime(2030, 12, 31) - datetime.datetime(1990, 1, 1)
    total_seconds = (period.days * 24 * 60 * 60) + period.seconds
    random_second = randrange(total_seconds)
    return datetime.datetime(1990, 1, 1, tzinfo=pytz.UTC) + datetime.timedelta(
        seconds=random_second
    )


def generate_body() -> RichText:
    body = ""
    for _ in range(randrange(1, 5)):  # no. paragraphs
        body += "<p>"
        for _ in range(randrange(1, 40)):  # no. sentences
            body += (
                gib.generate_word().title()
                + " "
                + (" ".join(gib.generate_words(randrange(1, 20)))).rstrip()
                + ". "
            )
        body += "</p>\n\n"

    return RichText(body)


def generate_summary() -> str:
    return (
        gib.generate_word().title()
        + " "
        + (" ".join(gib.generate_words(randrange(1, 20)))).rstrip()
        + "."
    )


def generate_image() -> str:
    # Adapted from here: https://techbeamers.com/generate-random-images-in-python/

    file_name = f"{gib.generate_word()}.png"

    width, height = 8, 8
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Generate and test random pixels
    for _ in range(10000):
        x = randint(0, width - 1)
        y = randint(0, height - 1)
        color = (randint(0, 255), randint(0, 255), randint(0, 255))
        draw.point((x, y), fill=color)

    image = image.resize((400, 400))

    try:
        image.save(f"media/original_images/{file_name}")
    except FileNotFoundError:
        os.makedirs("media/original_images")
        image.save(f"media/original_images/{file_name}")

    return file_name


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
                                    PageData(title="Aardvark", type=models.SupportTopicPage),
                                    PageData(title="Aeroplane", type=models.SupportTopicPage),
                                    PageData(title="Alligator", type=models.SupportTopicPage),
                                    PageData(title="Anchor", type=models.SupportTopicPage),
                                    PageData(title="Apple", type=models.SupportTopicPage),
                                    PageData(title="Astronaut", type=models.SupportTopicPage),
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
                                    PageData(title="Ball", type=models.SupportTopicPage),
                                    PageData(title="Banana", type=models.SupportTopicPage),
                                    PageData(title="Bear", type=models.SupportTopicPage),
                                    PageData(title="Book", type=models.SupportTopicPage),
                                    PageData(title="Bus", type=models.SupportTopicPage),
                                ],
                            ),
                            PageData(
                                title="Area C",
                                type=models.SupportAreaPage,
                                children=[
                                    PageData(title="Cat", type=models.SupportTopicPage),
                                    PageData(title="Cake", type=models.SupportTopicPage),
                                    PageData(title="Car", type=models.SupportTopicPage),
                                    PageData(title="Cave", type=models.SupportTopicPage),
                                    PageData(title="Carrot", type=models.SupportTopicPage),
                                    PageData(title="Chicken", type=models.SupportTopicPage),
                                    PageData(title="Cow", type=models.SupportTopicPage),
                                ],
                            ),
                        ],
                    ),
                    PageData(
                        title="News",
                        type=models.NewsPage,
                        children=[
                            PageData(title=gib.generate_word().title(), type=models.NewsArticlePage)
                            for i in range(10)
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
        page_data_dict = copy.deepcopy(page_data.__dict__)

        try:
            page = page_data.type.objects.get(title=page_data.title).specific
        except page_data.type.DoesNotExist:
            page_data_dict.pop("type", None)
            page_data_dict.pop("children", None)
            page_data_dict.pop("published", None)

            for content in page_data.type.__dict__["content_panels"]:
                name = content.field_name

                if name == "title":
                    page_data_dict[name] = page_data.title
                elif name == "body":
                    page_data_dict[name] = generate_body()
                elif name == "summary":
                    page_data_dict[name] = generate_summary()
                elif "image" in name:
                    file_name = generate_image()

                    img_bytes = open(f"media/original_images/{file_name}", "rb").read()
                    img_file = ImageFile(BytesIO(img_bytes), name=file_name)

                    image = WagtailImage(title=file_name, file=img_file)
                    image.save()

                    page_data_dict[name] = image

            if page_data.type == models.NewsArticlePage:
                published_date = generate_date()
                page_data_dict = page_data_dict | {
                    "first_published_at": published_date,
                    "latest_revision_created_at": published_date,
                    "last_published_at": published_date,
                }

            page = page_data.type(**page_data_dict)

            parent.add_child(instance=page)
            page.save()
            self.stdout.write(self.style.SUCCESS(f"{page.title} page created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"{page.title} already exists"))

        if page_data.children:
            for child_data in page_data.children:
                self.create_page(page, child_data)

        return page
