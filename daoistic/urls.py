""" Daoistic app URLs module. """
from django.urls import path
from daoistic import views


urlpatterns = [
    path('', views.PoemListView.as_view()),
    path('about', views.AboutTemplateView.as_view()),
    path('compare/<int:chapter>', views.ComparisonView.as_view(), name='compare'),
    path('nav/<int:current>/<direction>', views.NavJsonView.as_view()),
    path('poems', views.PoemListView.as_view()),
    path('poems/page/<int:page>', views.PoemListView.as_view()),
    path('poems/<int:chapter>', views.PoemDetailView.as_view(), name='poems'),
    path('studies', views.StudyListView.as_view()),
    path('search/<chars>', views.SearchBooksView.as_view()),
    path('search/<book>/<chars>', views.SearchChaptersView.as_view()),
    path('studies/page/<int:page>', views.StudyListView.as_view()),
    path('studies/<int:chapter>', views.StudyDetailView.as_view(), name='studies'),
]
