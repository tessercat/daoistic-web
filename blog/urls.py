""" Blog app URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path('', views.EntryListView.as_view(), name='blog'),
    path('<slug:slug>', views.PlainDetailView.as_view(), name='plain'),
    path('studies/<slug:slug>', views.StudyDetailView.as_view(), name='study'),
]
