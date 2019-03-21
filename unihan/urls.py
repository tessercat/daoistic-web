""" Unihan URLs module. """
from django.urls import path
from unihan import views


urlpatterns = [
    path('', views.DictionaryView.as_view()),
    path('dictionary', views.DictionaryView.as_view()),
    path('dump', views.DumpView.as_view()),
    path('info/<char>', views.CharDetailView.as_view()),
]
