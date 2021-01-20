""" Unihan sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class UnihanSitemap(Sitemap):
    """ Unihan sitemap URLs. """

    def items(self):
        """ Return entry objects. """
        # pylint: disable=no-self-use
        return ['lookup']

    def location(self, obj):
        """ Return entry location. """
        return reverse('unihan-lookup')
