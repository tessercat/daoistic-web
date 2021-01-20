""" Blog app URLs module. """
from django.urls import path
from blog import views


urlpatterns = [
    path(
        '',
        views.BlogList.as_view(),
        name='blog-list'
    ),
    path(
        'blog/<slug:slug>',
        views.EntryDetails.as_view(),
        name='blog-entry-plain'
    ),
    path(
        'blog/<slug:slug>/study',
        views.EntryDetails.as_view(),
        name='blog-entry-study'
    ),
    path(
        'archive/',
        views.ArchiveIndex.as_view(),
        name='blog-archive-index'
    ),
    path(
        'archive/<slug:slug>',
        views.ArchiveList.as_view(),
        name='blog-archive-list'
    ),
]
