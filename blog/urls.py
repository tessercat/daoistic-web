""" Blog app URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path('', views.BlogView.as_view()),
    path('blog/<slug:slug>', views.EntryView.as_view(), name='entry'),
    path('blog/<slug:slug>/study', views.EntryView.as_view(), name='study'),
    path('archive/', views.ArchiveIndexView.as_view(), name='archive_index'),
    path('archive/<slug:slug>', views.ArchiveView.as_view(), name='archive'),
]
