""" Blog app URLs module. """
from django.urls import path
from common import views


urlpatterns = [
    path('about', views.AboutView.as_view(), name='about'),
]
