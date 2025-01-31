from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from home.views import (accounts_page_view, catalogue_page_view,
                        workspaces_page_view)
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    re_path(
        r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
        ServeView.as_view(),
        name="wagtailimages_serve",
    ),
    re_path(r"^catalogue/.*$", catalogue_page_view),
    path("workspaces/", workspaces_page_view),
    path("accounts/", accounts_page_view),
    path("", include("core.urls")),
    path("", include("accounts.urls")),
    path("", include(wagtail_urls)),  # This entry should always be at the end of urlpatterns
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
