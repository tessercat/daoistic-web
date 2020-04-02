""" Project URL config module. """
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from blog.sitemaps import (
    BlogEntrySitemap,
    BlogPageSitemap,
    BlogStudySitemap,
)
from book.sitemaps import (
    BookPageSitemap,
    BookPoemSitemap,
    BookStudySitemap,
)
from book.views import bad_request, page_not_found


admin.site.site_header = 'Daoistic admin'
admin.site.site_title = 'Daoistic'


def custom400(request, exception):
    """ Return custom bad request. """
    # pylint: disable=unused-argument
    return bad_request(request)


def custom404(request, exception):
    """ Return custom bad request. """
    # pylint: disable=unused-argument
    return page_not_found(request)


handler400 = custom400
handler404 = custom404

urlpatterns = [
    path('', include('book.urls')),
    path('unihan/', include('unihan.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml', sitemap,
        {
            'sitemaps': {
                'book-pages': BookPageSitemap,
                'book-poems': BookPoemSitemap,
                'book-studies': BookStudySitemap,
                'blog-pages': BlogPageSitemap,
                'blog-entries': BlogEntrySitemap,
                'blog-studies': BlogStudySitemap,
            }
        },
        name='django.contrib.sitemaps.views.sitemap'
    )
]
