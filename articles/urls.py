from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_view, name="search"),
    path("compare/", views.compare_view, name="compare"),
]
