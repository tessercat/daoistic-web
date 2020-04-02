""" Blog app sitemaps module. """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Entry


class BlogEntrySitemap(Sitemap):
    """ Blog entry sitemap class. """

    def items(self):
        """ Return entry objects. """
        # pylint: disable=no-self-use
        return Entry.objects.filter(published=True)

    def lastmod(self, obj):
        """ Return entry lastmod. """
        # pylint: disable=no-self-use
        return obj.last_update

    def location(self, obj):
        """ Return entry location. """
        return '/blog/%s' % obj.slug


class BlogPageSitemap(Sitemap):
    """ Blog page sitemap class. """
    pages = ['blog']

    def items(self):
        """ Return page list. """
        # pylint: disable=no-self-use
        return self.pages

    def lastmod(self, obj):
        """ Return page lastmod. """
        # pylint: disable=no-self-use
        if obj == 'blog':
            return Entry.objects.filter(
                published=True
            ).latest('last_update').last_update
        return None

    def location(self, obj):
        """ Return page location. """
        return reverse(obj)


class BlogStudySitemap(Sitemap):
    """ Blog entry study sitemap class. """
    # pylint: disable=no-self-use

    def items(self):
        """ Return study objects. """
        # pylint: disable=no-self-use
        return Entry.objects.filter(published=True)

    def lastmod(self, obj):
        """ Return study lastmod. """
        # pylint: disable=no-self-use
        return obj.last_update

    def location(self, obj):
        """ Return study location. """
        return '/blog/studies/%s' % obj.slug
