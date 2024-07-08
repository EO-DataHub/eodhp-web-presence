from django.urls import path

from .views import catalogue_page_view

urlpatterns = [path("", catalogue_page_view, name="home/catalogue_page")]
