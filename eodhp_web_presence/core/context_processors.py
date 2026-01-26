from eodhp_web_presence import settings


def get_workspaces_ui_url(request):
    workspace = request.GET.get("workspace")
    if workspace:
        return f"/workspaces?workspace={workspace}"
    return "/workspaces"


def menu_links(request):
    return {
        "notebooks_url": settings.NOTEBOOKS["url"],
        "resource_catalogue_url": "/catalogue",
        "workspaces_ui_url": get_workspaces_ui_url(request),
    }
