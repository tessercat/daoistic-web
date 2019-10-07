""" Management utility to import blog from markdown. """
from datetime import datetime, timedelta, timezone
from shutil import copyfile
import os
from django.core.management.base import BaseCommand
from django.conf import settings
import sh
from blog.models import Entry


class Command(BaseCommand):
    """ A command to import blog data to the project db. """

    help = 'Used to import and update blog data.'
    requires_migrations_checks = True
    book_dir = os.path.join(settings.BASE_DIR, 'var', 'book')
    git = sh.git.bake(_cwd=book_dir, _tty_out=False)
    blog_dir = os.path.join(book_dir, 'blog')
    img_dir = os.path.join(settings.BASE_DIR, 'blog', 'static', 'blog', 'img')

    def handle(self, *args, **options):
        """ Import blog data. """

        # Get entry objects dict, delete objects with no dir.
        entry_dirs = os.listdir(self.blog_dir)
        entries = {}  # A dict of existing objects keyed by slug.
        for entry in Entry.objects.all():
            if entry.slug not in entry_dirs:
                entry.delete()
                print('Deleted', entry)
            else:
                entries[entry.slug] = entry

        # Create missing entries, update existing.
        for slug in entry_dirs:
            if slug in entries:
                self._update_entry(entries[slug])
            else:
                self._create_entry(slug)

    def _cp_static(self, slug):
        """ Copy card and header images to the blog app's static dir. """
        copyfile(
            os.path.join(self.blog_dir, slug, 'card.jpg'),
            os.path.join(self.img_dir, '%s-128.jpg' % slug)
        )
        copyfile(
            os.path.join(self.blog_dir, slug, 'header.jpg'),
            os.path.join(self.img_dir, '%s.jpg' % slug)
        )

    def _create_entry(self, slug):
        """ Create a new blog entry. """
        last_update = self._last_update(slug)
        if last_update:
            lede = self._lede(slug)
            published = lede is not None
            title = self._title(slug)
            entry = Entry.objects.create(
                last_update=last_update,
                lede=lede,
                published=published,
                slug=slug,
                title=title,
            )
            self._cp_static(slug)
            print('Created', entry)

    def _git_log_date(self, slug, filename):
        """ Return a datetime for the file from git log. """
        result = self.git.log(
            '-1', '--format=%ad', '--date=raw', '--',
            'blog/%s/%s' % (slug, filename)
        )
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

    def _last_update(self, slug):
        """ Return a datetime object for last_update field or None. """
        content_date = self._git_log_date(slug, 'content.md')
        notes_date = self._git_log_date(slug, 'notes.md')
        if content_date and notes_date:
            if content_date > notes_date:
                return content_date
            return notes_date
        if content_date:
            return content_date
        return None

    def _lede(self, slug):
        """ Return a string for the lede field. """
        path = os.path.join(self.blog_dir, slug, 'lede.md')
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.read()
        return None

    def _title(self, slug):
        """ Return a string for the title field. """
        path = os.path.join(self.blog_dir, slug, 'content.md')
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.readline()[2:]
        return None

    def _update_entry(self, entry):
        """ Update an existing blog entry. """
        last_update = self._last_update(entry.slug)
        if last_update:
            lede = self._lede(entry.slug)
            published = lede is not None
            title = self._title(entry.slug)
        entry.last_update = last_update
        entry.lede = lede
        entry.published = published
        entry.title = title
        entry.save()
        self._cp_static(entry.slug)
        print('Updated', entry)
