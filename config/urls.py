""" Project URL config module. """
from django.contrib import admin
from django.urls import include, path


admin.site.site_header = 'Daoistic administration'
admin.site.site_title = 'Daoistic'

urlpatterns = [
    path('', include('daoistic.urls')),
    path('unihan/', include('unihan.urls')),
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
]
