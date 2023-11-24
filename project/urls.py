""" Project URL config module. """
from django.contrib import admin
from django.urls import include, path
from common.views import custom400
from common.views import custom404


admin.site.site_header = 'Daoistic admin'
admin.site.site_title = 'Daoistic'

handler400 = custom400
handler404 = custom404

urlpatterns = [
    path('', include('entry.urls')),
    path('', include('common.urls')),
    path('unihan', include('unihan.urls')),
    path('admin/', admin.site.urls),
]
