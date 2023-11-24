""" Entry sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from entry.models import Archive, Entry


class EntrySitemap(Sitemap):
    """ Entry sitemap URLs. """

    def items(self):
        """ Return entry objects. """
        entries = Entry.objects.filter(
            published=True
        ).order_by('-last_update')
        archives = Archive.objects.all().order_by('slug')
        return list(archives) + list(entries)

    def lastmod(self, item):
        """ Return entry lastmod. """
        if isinstance(item, Entry):
            return item.last_update
        return None

    def location(self, item):
        """ Return entry location. """
        if isinstance(item, Entry):
            return reverse('entry-plain', args=[item.slug])
        if isinstance(item, Archive):
            return reverse('archive-list', args=[item.slug])
        return None
