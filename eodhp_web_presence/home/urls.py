from django.urls import path

from .views import get_temp_credentials

urlpatterns = [
    path("get_credentials/", get_temp_credentials, name="get_credentials"),
    path(
        "refresh_credentials/", get_temp_credentials, name="refresh_credentials"
    ),  # TODO: Implement refresh_credentials
    # path('revoke_credentials/', views.revoke_credentials, name='revoke_credentials'), # TODO: Implement
]
