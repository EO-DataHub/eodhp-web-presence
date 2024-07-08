from django.urls import path

from .views import catalogue_page_view, search_topics, search_topics_blank

urlpatterns = [
    path("", catalogue_page_view, name="home/catalogue_page"),
    path("search_items", search_topics, name="search_topics"),
    path("search_items_blank", search_topics_blank, name="search_topics_blank"),
]
