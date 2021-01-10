""" Common sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class CommonSitemap(Sitemap):
    """ Common sitemap URLs. """

    def items(self):
        """ Return entry objects. """
        # pylint: disable=no-self-use
        return ['about']

    def location(self, obj):
        """ Return entry location. """
        return reverse('about')
