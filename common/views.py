""" Common views module. """
import os
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
from common.apps import common_settings
from common.decorators import cache_public


def custom400(request, exception):
    """ Custom 400. """
    # pylint: disable=unused-argument
    return HttpResponseBadRequest(render(
        request,
        'common/error.html',
        {
            'css': common_settings.get('css'),
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
            'css': common_settings.get('css'),
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
            'css': common_settings.get('css'),
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
        context['css'] = common_settings.get('css')
        return context

    def about(self):
        """ Return about page HTML content. """
        # pylint: disable=no-self-use
        path = os.path.join(
            settings.BASE_DIR, 'var', 'data', 'about.md',
        )
        with open(path) as about_fd:
            return markdown.markdown(about_fd.read())
