""" Common app URLs module. """
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from entry.sitemaps import EntrySitemap
from unihan.sitemaps import UnihanSitemap
from common import views
from common.sitemaps import CommonSitemap


urlpatterns = [
    path('about', views.AboutView.as_view(), name='common-about'),
    path(
        'sitemap.xml',
        sitemap,
        {
            'sitemaps': {
                'common': CommonSitemap,
                'unihan': UnihanSitemap,
                'entry': EntrySitemap
            }
        },
        name='django.contrib.sitemaps.views.sitemap'
    )
]
