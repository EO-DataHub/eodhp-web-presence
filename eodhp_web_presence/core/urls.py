from django.urls import path

from . import views
from .robots import robots_txt

urlpatterns = [
    path("authenticated/", views.authenticated, name="authenticated"),
    path("robots.txt", robots_txt),
]
