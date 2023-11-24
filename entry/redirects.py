""" Entry app redirects module. """
from django.views.generic.base import RedirectView


class BlogPlainRedirect(RedirectView):
    """ Blog plain redirect. """
    pattern_name = 'entry-plain'


class BlogStudyRedirect(RedirectView):
    """ Blog study redirect. """
    pattern_name = 'entry-study'


class ArticlePlainRedirect(RedirectView):
    """ Article plain redirect. """
    pattern_name = 'entry-plain'


class ArticleStudyRedirect(RedirectView):
    """ Article study redirect. """
    pattern_name = 'entry-study'
