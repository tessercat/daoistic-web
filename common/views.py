""" Common views module. """
from fnmatch import fnmatch
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
from common.decorators import cache_public


def css_file():
    """ Return the name of the hashed css file. """
    pattern = 'daoistic.?????.css'
    app_dir = os.path.join(
        settings.BASE_DIR,
        'common', 'static', 'common', 'css'
    )
    for filename in os.listdir(app_dir):
        if fnmatch(filename, pattern):
            return filename
    return None


def unihan_script():
    """ Return the name of the hashed script file. """
    pattern = 'daoistic.?????.js'
    app_dir = os.path.join(
        settings.BASE_DIR,
        'common', 'static', 'common', 'js'
    )
    for filename in os.listdir(app_dir):
        if fnmatch(filename, pattern):
            return filename
    return None


@method_decorator(cache_public(60 * 15), name='dispatch')
def custom400(request, exception):
    """ Custom 400. """
    # pylint: disable=unused-argument
    return HttpResponseBadRequest(render(
        request,
        'common/error.html',
        {
            'css_file': css_file(),
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
            'css_file': css_file(),
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
            'css_file': css_file(),
            'message': 'Not Found',
            'page_title': '404 Not Found',
        },
    ))


class AboutView(TemplateView):
    """ About Daoistic view. """
    template_name = 'blog/about.html'

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About Daoistic'
        context['css_file'] = css_file()
        return context

    def about(self):
        """ Return about page HTML content. """
        # pylint: disable=no-self-use
        path = os.path.join(
            settings.BASE_DIR, 'var', 'data', 'about.md',
        )
        with open(path) as about_fd:
            return markdown.markdown(about_fd.read())
