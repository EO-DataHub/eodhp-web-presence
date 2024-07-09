from django.urls import path

from .views import search_topics

urlpatterns = [
    path("search_items", search_topics, name="search_topics"),
]
