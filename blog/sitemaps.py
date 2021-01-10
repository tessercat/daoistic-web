""" Blog sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Entry


class BlogSitemap(Sitemap):
    """ Blog sitemap URLs. """

    def items(self):
        """ Return entry objects. """
        return Entry.objects.filter(published=True).order_by('-last_update')

    def lastmod(self, obj):
        """ Return entry lastmod. """
        # pylint: disable=no-self-use
        return obj.last_update

    def location(self, obj):
        """ Return entry location. """
        return reverse('entry', args=[obj.slug])
