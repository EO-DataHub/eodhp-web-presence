from django.urls import path

from .views import catalogue_page_view, search_topics

urlpatterns = [
    path("search_items", search_topics, name="search_topics"),
]
