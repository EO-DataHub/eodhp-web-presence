from eodhp_web_presence import settings


def menu_links(request):
    return {
        "notebooks_url": "https://{workspace}.dev.eodatahub-workspaces.org.uk/notebooks",
        "resource_catalogue_url": "/catalogue",
        "workspaces_ui_url": "/workspaces",
    }
