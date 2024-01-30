from django.urls import include, path
from .views import help_page_view

urlpatterns = [
    path('', help_page_view, name='help/help_page')
]
