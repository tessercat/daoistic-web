""" Daoistic URLs module. """
from django.urls import path
from daoistic import views


urlpatterns = [
    path('', views.PoemListView.as_view()),
    path('about', views.AboutTemplateView.as_view()),
    path('compare/chapter/<int:chapter>', views.ComparisonView.as_view()),
    path('nav/<int:current>/<direction>', views.NavJsonView.as_view()),
    path('poems', views.PoemListView.as_view()),
    path('poems/page/<int:page>', views.PoemListView.as_view()),
    path('poems/chapter/<int:chapter>', views.PoemDetailView.as_view()),
    path('studies', views.StudyListView.as_view()),
    path('search/<chars>', views.SearchBooksView.as_view()),
    path('search/<book>/<chars>', views.SearchChaptersView.as_view()),
    path('studies/page/<int:page>', views.StudyListView.as_view()),
    path('studies/chapter/<int:chapter>', views.StudyDetailView.as_view()),
]
