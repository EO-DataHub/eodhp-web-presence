from django.test import TestCase

from home.templatetags.bg_tags import bg_classes


class BgClassesTests(TestCase):
    def test_valid_color(self):
        assert bg_classes("navy") == "bg--navy"

    def test_valid_color_full_width(self):
        assert bg_classes("navy", full_width=True) == "bg--navy bg-full-width"

    def test_default_returns_empty(self):
        assert bg_classes("default") == ""

    def test_default_full_width_returns_empty(self):
        assert bg_classes("default", full_width=True) == ""

    def test_blank_returns_empty(self):
        assert bg_classes("") == ""

    def test_none_returns_empty(self):
        assert bg_classes(None) == ""

    def test_blank_full_width_returns_empty(self):
        assert bg_classes("", full_width=True) == ""
