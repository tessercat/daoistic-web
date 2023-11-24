""" Entry app URLs module. """
from django.urls import path
from entry import views, redirects


urlpatterns = [
    path(
        '',
        views.ArchiveIndex.as_view(),
        name='archive-index'
    ),
    path(
        'tag/<slug:slug>',
        views.ArchiveList.as_view(),
        name='archive-list'
    ),
    path(
        'entry/<slug:slug>',
        views.EntryDetails.as_view(),
        name='entry-plain'
    ),
    path(
        'entry/<slug:slug>/study',
        views.EntryDetails.as_view(),
        name='entry-study'
    ),
    path(
        'blog/',
        views.BlogIndex.as_view(),
        name='blog-index'
    ),
    path(
        'rss',
        views.BlogFeed(),
        name='blog-rss'
    ),
    path(
        'blog/<slug:slug>',
        redirects.BlogPlainRedirect.as_view(),
        name='redirect-blog-plain'
    ),
    path(
        'blog/<slug:slug>/study',
        redirects.BlogStudyRedirect.as_view(),
        name='redirect-blog-study'
    ),
    path(
        'article/<slug:slug>',
        redirects.ArticlePlainRedirect.as_view(),
        name='redirect-article-plain'
    ),
    path(
        'article/<slug:slug>/study',
        redirects.ArticleStudyRedirect.as_view(),
        name='redirect-article-study'
    ),
]
