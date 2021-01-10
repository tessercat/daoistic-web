""" Blog app URLs module. """
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from blog.sitemaps import BlogSitemap
from common import views
from common.sitemaps import CommonSitemap
from unihan.sitemaps import UnihanSitemap


urlpatterns = [
    path('about', views.AboutView.as_view(), name='about'),
    path(
        'sitemap.xml',
        sitemap,
        {
            'sitemaps': {
                'common': CommonSitemap,
                'unihan': UnihanSitemap,
                'blog': BlogSitemap
            }
        },
        name='django.contrib.sitemaps.views.sitemap'
    )
]
