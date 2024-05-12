from eodhp_web_presence import settings


def menu_links(request):
    return {
        'menu_links': {
            "resource_catalogue_url": "/catalogue",
            "eox_viewserver_url": settings.EOX_VIEWSERVER["url"],
            "documentation_url": settings.DOCUMENTATION["url"],
            "notebooks_url": settings.NOTEBOOKS["url"],
        }
    }