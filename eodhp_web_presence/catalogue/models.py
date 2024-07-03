from wagtail.models import Page
from wagtailcache.cache import WagtailCacheMixin


class CataloguePage(Page):
    content_panels = Page.content_panels


class FakeCataloguePage(WagtailCacheMixin, Page):
    content_panels = Page.content_panels

    template = "fake-catalogue/map-search.html"
