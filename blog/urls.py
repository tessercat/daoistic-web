""" Unihan URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path('<slug:slug>', views.EntryView.as_view()),
]
