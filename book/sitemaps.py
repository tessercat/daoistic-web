""" Book app sitemaps module. """
import os
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
import sh
from book.models import Chapter


class BookPageSitemap(Sitemap):
    """ Book page sitemap class. """
    book_dir = os.path.join(settings.BASE_DIR, 'var', 'book')
    git = sh.git.bake(_cwd=book_dir, _tty_out=False)
    pages = ['about']

    def _page_datetime(self, page):
        """ Return git log datetime for a page file. """
        filename = os.path.join(self.book_dir, '%s.md' % page)
        cmd = ['-1', '--format=%ad', '--date=raw', '--', filename]
        result = self.git.log(cmd)
        if result:
            parts = result.stdout.decode().strip().split()
            return datetime.fromtimestamp(
                int(parts[0]),
                timezone(
                    timedelta(
                        hours=int(parts[1][0:3]),
                        minutes=int(parts[1][3:5])
                    )
                ),
            )
        return None

    def items(self):
        """ Return page list. """
        # pylint: disable=no-self-use
        return self.pages

    def lastmod(self, obj):
        """ Return page lastmod. """
        if obj in self.pages:
            return self._page_datetime(obj)
        return None

    def location(self, obj):
        """ Return page location. """
        return reverse(obj)


class BookPoemSitemap(Sitemap):
    """ Book poem sitemap class. """

    def items(self):
        """ Return poem objects. """
        # pylint: disable=no-self-use
        return Chapter.objects.filter(book__title='道德經', published=True)

    def lastmod(self, obj):
        """ Return poem lastmod. """
        # pylint: disable=no-self-use
        return obj.last_english_update

    def location(self, obj):
        """ Return poem location. """
        return '/poems/%d' % obj.number


class BookStudySitemap(Sitemap):
    """ Book study sitemap class. """

    def items(self):
        """ Return study objects. """
        # pylint: disable=no-self-use
        return Chapter.objects.filter(book__title='道德經', published=True)

    def lastmod(self, obj):
        """ Return study lastmod. """
        # pylint: disable=no-self-use
        if obj.last_english_update > obj.last_hanzi_update:
            return obj.last_english_update
        return obj.last_hanzi_update

    def location(self, obj):
        """ Return study location. """
        return '/studies/%d' % obj.number
