""" Common views module. """
import markdown
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from common.decorators import cache_public


def custom400(request, exception):
    """ Custom 400. """
    # pylint: disable=unused-argument
    return HttpResponseBadRequest(render(
        request,
        'common/error.html',
        {
            'message': 'Bad Request',
            'page_title': '400 Bad Request',
        },
    ))


def custom403(request, reason=''):
    """ Custom 403. """
    # pylint: disable=unused-argument
    return HttpResponseForbidden(render(
        request,
        'common/error.html',
        {
            'message': 'Forbidden',
            'page_title': '403 Forbidden',
        },
    ))


def custom404(request, exception):
    """ Custom 404. """
    # pylint: disable=unused-argument
    return HttpResponseNotFound(render(
        request,
        'common/error.html',
        {
            'message': 'Not Found',
            'page_title': '404 Not Found',
        },
    ))


@method_decorator(cache_public(60 * 15), name='dispatch')
class AboutView(TemplateView):
    """ About Daoistic view. """
    template_name = 'common/about.html'

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About Daoistic'
        return context

    def about(self):
        """ Return about page HTML content. """
        path = settings.BASE_DIR / 'var' / 'data' / 'about.md'
        with open(path, encoding='utf-8') as about_fd:
            return markdown.markdown(about_fd.read())
