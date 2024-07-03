from django.urls import path

from . import views

urlpatterns = [
    path("search_items", views.search_topics, name="search_topics"),
    path("search_items_blank", views.search_topics_blank, name="search_topics_blank"),
]
