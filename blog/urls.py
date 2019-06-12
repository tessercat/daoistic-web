""" Unihan URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path('', views.EntryListView.as_view()),
    path('<slug:slug>', views.EntryDetailView.as_view(), name='entry'),
]
