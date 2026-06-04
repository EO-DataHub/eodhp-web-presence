import re

from django.contrib.auth.models import AnonymousUser, User
from django.template.loader import render_to_string
from django.test import SimpleTestCase, override_settings


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class TestMenuTemplate(SimpleTestCase):
    def render_menu(self, user=None) -> str:
        return render_to_string(
            "menu.html",
            {
                "user": user or AnonymousUser(),
                "notebooks_url": "/notebooks",
                "workspaces_ui_url": "/workspaces",
                "userdocs_url": "https://docs.example.com",
            },
        )

    def test_dropdown_parent_destinations_are_child_links(self):
        html = self.render_menu()

        assert '<span class="dropdown__label">About</span>' in html
        assert '<a href="/about/">About EO Data Hub</a>' in html
        assert '<span class="dropdown__label">Data</span>' in html
        assert '<a href="/data/">All Data</a>' in html
        assert '<span class="dropdown__label">Getting Started</span>' in html
        assert '<a href="/docs/">Start Here</a>' in html

    def test_dropdown_parents_render_as_accessible_buttons(self):
        html = self.render_menu()

        expected_menu_ids = {
            "about-menu",
            "data-menu",
            "getting-started-menu",
            "catalogue-menu-mobile",
            "catalogue-menu-desktop",
        }

        controlled_menu_ids = set(re.findall(r'aria-controls="([^"]+)"', html))
        rendered_menu_ids = set(re.findall(r'id="([^"]+-menu(?:-[^"]+)?)"', html))

        assert expected_menu_ids <= controlled_menu_ids
        assert expected_menu_ids <= rendered_menu_ids

        for menu_id in expected_menu_ids:
            assert (
                f'<button type="button" class="dropdown__toggle" aria-expanded="false" aria-controls="{menu_id}"'
            ) in html

    def test_catalogue_uses_existing_browse_link_without_parent_link_duplicate(self):
        html = self.render_menu()

        assert '<span class="dropdown__label">Catalogue</span>' in html
        assert html.count('<a href="/static-apps/sg-rc-ui/prod/index.html#/">Browse</a>') == 2
        assert '<a href="/static-apps/sg-rc-ui/prod/index.html#/">Catalogue</a>' not in html

    def test_authenticated_account_menus_are_accessible_buttons(self):
        html = self.render_menu(User(username="test-user"))

        assert (
            '<button type="button" class="dropdown__toggle" aria-expanded="false" aria-controls="account-menu-mobile">'
        ) in html
        assert (
            '<button type="button" class="dropdown__toggle" aria-expanded="false" '
            'aria-controls="account-menu-desktop" aria-label="Account menu">'
        ) in html
        assert '<a href="/accounts">test-user</a>' in html
