from django.urls import path

from . import views

urlpatterns = [
    path("sign_in/", views.sign_in, name="sign_in"),
    path("sign_out/", views.sign_out, name="sign_out"),
    path("accounts/kc-action/callback/", views.keycloak_action_callback, name="keycloak_action_callback"),
    path("accounts/kc-action/<str:action>/", views.keycloak_action, name="keycloak_action"),
]
