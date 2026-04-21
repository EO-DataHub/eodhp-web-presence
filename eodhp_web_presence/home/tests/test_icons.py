from django.test import SimpleTestCase
from draftjs_exporter.dom import DOM

from home.icons import get_icon_path
from home.mdi import clean_name, clean_size
from home.templatetags.mdi_tags import inject_mdi_icons, mdi_icon
from home.wagtail_hooks import ICON_ENTITY_TYPE, IconEntityElementHandler, icon_entity
from home.widgets import IconPickerWidget


class GetIconPathTests(SimpleTestCase):
    def test_known_icon_returns_path(self) -> None:
        d = get_icon_path("account")
        assert isinstance(d, str)
        assert d.startswith("M")

    def test_unknown_icon_returns_none(self) -> None:
        assert get_icon_path("does-not-exist-here") is None


class IconEntityExporterTests(SimpleTestCase):
    def setUp(self) -> None:
        DOM.use(DOM.STRING)

    def _export(self, props: dict) -> str:
        return DOM.render(icon_entity(props))

    def test_valid_icon_emits_span_without_svg(self) -> None:
        html = self._export({"name": "account", "size": "md", "children": "\u200b"})
        assert 'data-mdi-icon="account"' in html
        assert 'data-mdi-size="md"' in html
        assert 'class="mdi mdi-account"' in html
        assert "<svg" not in html
        assert "\u200b" in html

    def test_unknown_icon_keeps_entity_shape(self) -> None:
        html = self._export({"name": "totally-made-up-name", "size": "sm", "children": "\u200b"})
        assert "<svg" not in html
        assert 'data-mdi-icon="totally-made-up-name"' in html

    def test_invalid_name_emits_sanitised_shell(self) -> None:
        html = self._export({"name": "<script>", "size": "sm", "children": "\u200b"})
        assert "<svg" not in html
        assert "<script" not in html
        assert 'data-mdi-icon=""' in html

    def test_invalid_size_falls_back_to_sm(self) -> None:
        html = self._export({"name": "account", "size": "huge", "children": "\u200b"})
        assert 'data-mdi-size="sm"' in html


class IconEntityElementHandlerTests(SimpleTestCase):
    def setUp(self) -> None:
        self.handler = IconEntityElementHandler(ICON_ENTITY_TYPE)

    def test_valid_attrs_round_trip(self) -> None:
        data = self.handler.get_attribute_data({"data-mdi-icon": "account", "data-mdi-size": "md"})
        assert data == {"name": "account", "size": "md"}

    def test_missing_size_defaults_to_sm(self) -> None:
        data = self.handler.get_attribute_data({"data-mdi-icon": "account"})
        assert data == {"name": "account", "size": "sm"}

    def test_missing_name_is_empty(self) -> None:
        data = self.handler.get_attribute_data({"data-mdi-size": "lg"})
        assert data == {"name": "", "size": "lg"}

    def test_malformed_name_is_stripped(self) -> None:
        for bad in ("<script>", "Account", "account--bad", "-account", "account-"):
            data = self.handler.get_attribute_data({"data-mdi-icon": bad, "data-mdi-size": "sm"})
            assert data["name"] == "", f"expected '' for {bad!r}, got {data['name']!r}"

    def test_unknown_size_falls_back_to_sm(self) -> None:
        data = self.handler.get_attribute_data({"data-mdi-icon": "account", "data-mdi-size": "huge"})
        assert data == {"name": "account", "size": "sm"}

    def test_empty_attrs(self) -> None:
        assert self.handler.get_attribute_data({}) == {"name": "", "size": "sm"}


class InjectMdiIconsFilterTests(SimpleTestCase):
    def test_span_without_data_mdi_icon_untouched(self) -> None:
        html = '<span class="foo">bar</span>'
        assert inject_mdi_icons(html) == html

    def test_non_icon_html_passes_through(self) -> None:
        html = "<p>Hello world</p>"
        assert inject_mdi_icons(html) == html

    def test_empty_string(self) -> None:
        assert inject_mdi_icons("") == ""

    def test_valid_icon_gets_svg_injected(self) -> None:
        html = (
            '<span class="mdi mdi-account" aria-hidden="true" data-mdi-icon="account" data-mdi-size="md">\u200b</span>'
        )
        result = inject_mdi_icons(html)
        assert "<svg" in result
        assert 'viewBox="0 0 24 24"' in result
        assert 'fill="currentColor"' in result
        assert "<path" in result
        assert 'data-mdi-icon="account"' in result

    def test_unknown_icon_left_unchanged(self) -> None:
        html = '<span data-mdi-icon="nonexistent-icon">\u200b</span>'
        result = inject_mdi_icons(html)
        assert "<svg" not in result

    def test_span_with_existing_svg_is_idempotent(self) -> None:
        html = (
            '<span data-mdi-icon="account" data-mdi-size="md">'
            '\u200b<svg viewBox="0 0 24 24" fill="currentColor">'
            '<path d="M12"/></svg></span>'
        )
        result = inject_mdi_icons(html)
        assert result == html

    def test_multiple_icons_in_one_block(self) -> None:
        html = (
            "<p>"
            '<span data-mdi-icon="account" data-mdi-size="sm">\u200b</span>'
            " and "
            '<span data-mdi-icon="account" data-mdi-size="lg">\u200b</span>'
            "</p>"
        )
        result = inject_mdi_icons(html)
        assert result.count("<svg") == 2

    def test_invalid_name_in_stored_html_is_skipped(self) -> None:
        html = '<span data-mdi-icon="&lt;script&gt;">\u200b</span>'
        result = inject_mdi_icons(html)
        assert "<svg" not in result
        assert "<script" not in result


class ValidatorTests(SimpleTestCase):
    def test_clean_name_accepts_valid(self) -> None:
        for ok in ("account", "account-outline", "abc123", "a", "a1-b2-c3"):
            assert clean_name(ok) == ok, f"expected {ok!r} unchanged"

    def test_clean_name_rejects_invalid(self) -> None:
        for bad in (
            "",
            "Account",
            "account--bad",
            "-account",
            "account-",
            "account ",
            "account_outline",
            "<script>",
            None,
            123,
            True,
        ):
            assert clean_name(bad) == "", f"expected '' for {bad!r}"

    def test_clean_size_accepts_valid(self) -> None:
        for ok in ("sm", "md", "lg", "xl"):
            assert clean_size(ok) == ok

    def test_clean_size_rejects_invalid(self) -> None:
        for bad in ("", "SM", "huge", " sm", "sm ", None, 0, True):
            assert clean_size(bad) == "sm", f"expected 'sm' default for {bad!r}"


class MdiIconTagTests(SimpleTestCase):
    def test_valid_icon_renders_svg(self) -> None:
        result = mdi_icon("account", "md")
        assert "<svg" in result
        assert 'class="mdi mdi-account"' in result
        assert 'data-mdi-icon="account"' in result
        assert 'data-mdi-size="md"' in result
        assert 'aria-hidden="true"' in result

    def test_default_size_is_sm(self) -> None:
        result = mdi_icon("account")
        assert 'data-mdi-size="sm"' in result

    def test_unknown_icon_returns_empty_string(self) -> None:
        assert mdi_icon("nonexistent-xyz") == ""

    def test_invalid_name_returns_empty_string(self) -> None:
        assert mdi_icon("") == ""
        assert mdi_icon("<script>") == ""

    def test_invalid_size_falls_back_to_sm(self) -> None:
        result = mdi_icon("account", "huge")
        assert 'data-mdi-size="sm"' in result


class IconPickerWidgetTests(SimpleTestCase):
    def test_media_includes_icon_field_js(self) -> None:
        widget = IconPickerWidget()
        assert "bundles/icon-field.js" in widget.media._js

    def test_is_text_input(self) -> None:
        widget = IconPickerWidget()
        assert widget.is_hidden is False
        html = widget.render("icon_name", "")
        assert 'type="text"' in html

    def test_value_rendered_in_input(self) -> None:
        widget = IconPickerWidget()
        html = widget.render("icon_name", "rocket-launch")
        assert "rocket-launch" in html
