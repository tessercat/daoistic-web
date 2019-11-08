""" Project URL config module. """
from django.contrib import admin
from django.urls import include, path
from book.views import bad_request, page_not_found


admin.site.site_header = 'Daoistic admin'
admin.site.site_title = 'Daoistic'


def custom400(request, exception):
    """ Return custom bad request. """
    return bad_request(request)


def custom404(request, exception):
    """ Return custom bad request. """
    return page_not_found(request)


handler400 = custom400
handler404 = custom404


urlpatterns = [
    path('', include('book.urls')),
    path('unihan/', include('unihan.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
]
