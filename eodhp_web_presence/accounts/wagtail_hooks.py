from django.conf import settings
from django.http import HttpRequest
from django.urls import URLPattern, path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from . import views
from .permissions import is_hub_admin


class HubUsersMenuItem(MenuItem):
    def is_shown(self, request: HttpRequest) -> bool:
        return bool(settings.KEYCLOAK["USER_LIST_ENABLED"]) and is_hub_admin(request)


@hooks.register("register_admin_urls")
def register_hub_users_urls() -> list[URLPattern]:
    return [
        path("hub-users/", views.hub_users_index, name="hub_users_index"),
        path("hub-users/export.csv", views.hub_users_export, name="hub_users_export"),
    ]


@hooks.register("register_admin_menu_item")
def register_hub_users_menu_item() -> MenuItem:
    return HubUsersMenuItem("Hub users", reverse("hub_users_index"), icon_name="group", order=10000)
