""" Unihan URLs module. """
from django.urls import path
from unihan import views


urlpatterns = [
    path('', views.UnihanFormView.as_view(), name='unihan-lookup'),
]
