""" Project URL config module. """
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = 'Daoistic admin'
admin.site.site_title = 'Daoistic'

urlpatterns = [
    path('', include('book.urls')),
    path('unihan/', include('unihan.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
]
