import logging
from urllib.parse import urlencode

from django.http import HttpRequest
from home.models import NotificationBanner

from eodhp_web_presence import settings

logger = logging.getLogger(__name__)


def get_workspaces_ui_url(request: HttpRequest) -> str:
    workspace = request.GET.get("workspace")
    if workspace:
        return f"/workspaces?{urlencode({'workspace': workspace})}"
    return "/workspaces"


def menu_links(request: HttpRequest) -> dict[str, str]:
    userdocs_base = settings.USERDOCS["base_url"]
    return {
        "notebooks_url": settings.NOTEBOOKS["url"],
        "resource_catalogue_url": "/catalogue",
        "workspaces_ui_url": get_workspaces_ui_url(request),
        "userdocs_url": userdocs_base,
        "userdocs_faqs_url": userdocs_base + settings.USERDOCS["faqs"],
        "userdocs_accounts_url": userdocs_base + settings.USERDOCS["user_accounts"],
        "userdocs_community_url": userdocs_base + settings.USERDOCS["community"],
        "github_org_url": settings.SOCIALS["github_org_url"],
        "github_discussions_url": settings.SOCIALS["github_discussions_url"],
        "linkedin_url": settings.SOCIALS["linkedin_url"],
    }


def notification_banner(request: HttpRequest) -> dict[str, object]:
    banner = NotificationBanner.get_active_banner()
    return {"notification_banner": banner}
