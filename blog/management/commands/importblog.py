""" Management utility to import blog from markdown. """
from datetime import date
import filecmp
import os
from shutil import copyfile
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

    def _cp_static(self, slug):
        """ Copy card and header images to the blog app's static dir. """
        changed = False
        src = os.path.join(self.blog_dir, slug, 'card.jpg')
        dst = os.path.join(self.img_dir, '%s-128.jpg' % slug)
        if not filecmp.cmp(src, dst):
            copyfile(src, dst)
            changed = True
        src = os.path.join(self.blog_dir, slug, 'header.jpg')
        dst = os.path.join(self.img_dir, '%s.jpg' % slug)
        if not filecmp.cmp(src, dst):
            copyfile(src, dst)
            changed = True
        return changed

    def _create(self, slug):
        """ Create a new blog entry. """
        first_published = self._first_published(slug)
        last_update = self._last_update(slug)
        if last_update:
            lede = self._lede(slug)
            published = lede is not None
            title = self._title(slug)
            entry = Entry.objects.create(
                first_published=first_published,
                last_update=last_update,
                lede=lede,
                published=published,
                slug=slug,
                title=title,
            )
            self._cp_static(slug)
            print('Created', entry.slug)

    def _date(self, slug, filename, reverse=False):
        """ Return a date for the file from git log. """
        cmd = [
            '--format=%ad', '--date=raw', '--',
            'blog/%s/%s' % (slug, filename),
        ]
        if reverse:
            cmd.insert(0, '--reverse')
            # pylint: disable=no-member
            result = sh.head(self.git.log(cmd), -1)
        else:
            cmd.insert(0, '-1')
            result = self.git.log(cmd)
        if result:
            parts = result.stdout.decode().strip().split()
            return date.fromtimestamp(int(parts[0]))
        return None

    def _first_published(self, slug):
        """ Return a date object for first_published field or None. """
        return self._date(slug, 'content.md', True)

    def _last_update(self, slug):
        """ Return a date object for last_update field or None. """
        content_date = self._date(slug, 'content.md')
        notes_date = self._date(slug, 'notes.md')
        if content_date and notes_date:
            if content_date > notes_date:
                return content_date
            return notes_date
        return content_date

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

    def _update(self, entry):
        """ Update an existing blog entry. """
        data = {}
        data['last_update'] = self._last_update(entry.slug)
        if data['last_update']:
            data['lede'] = self._lede(entry.slug)
            data['published'] = data['lede'] is not None
            data['title'] = self._title(entry.slug)
        changed = False
        for key, value in data.items():
            if getattr(entry, key) != value:
                setattr(entry, key, value)
                changed = True
        if changed:
            entry.save()
            print('Updated', entry.slug)

    def handle(self, *args, **options):
        """ Import blog data. """

        # Get entry objects dict, delete objects with no dir.
        entry_dirs = os.listdir(self.blog_dir)
        entries = {}  # A dict of existing objects keyed by slug.
        for entry in Entry.objects.all():
            if entry.slug not in entry_dirs:
                entry.delete()
                print('Deleted', entry.slug)
            else:
                entries[entry.slug] = entry

        # Create missing entries, update existing.
        for slug in entry_dirs:
            if slug in entries:
                self._update(entries[slug])
            else:
                self._create(slug)
