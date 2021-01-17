""" Blog app URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path(
        '',
        views.BlogView.as_view(),
        name='blog_index'
    ),
    path(
        'blog/<slug:slug>',
        views.EntryView.as_view(),
        name='blog_entry'
    ),
    path(
        'blog/<slug:slug>/study',
        views.EntryView.as_view(),
        name='blog_study'
    ),
    path(
        'archive/',
        views.ArchiveView.as_view(),
        name='archive_index'
    ),
    path(
        'archive/<slug:slug>',
        views.ArchiveDirectoryView.as_view(),
        name='archive_directory'
    ),
]
