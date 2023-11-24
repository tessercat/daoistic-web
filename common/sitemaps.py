""" Common sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class CommonSitemap(Sitemap):
    """ Common sitemap URLs. """

    def items(self):
        """ Return sitemap objects. """
        return ['about']

    def location(self, item):
        """ Return item location. """
        return reverse('common-about')
