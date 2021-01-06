""" Management utility to import blog from markdown. """
import ast
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
    data_dir = os.path.join(settings.BASE_DIR, 'var', 'data')
    git = sh.git.bake(_cwd=data_dir, _tty_out=False)
    blog_dir = os.path.join(data_dir, 'blog')
    img_dir = os.path.join(
        settings.BASE_DIR, 'blog', 'static', 'blog', 'img'
    )

    def _cp_static(self, archive, slug, jpg, resolution=None):
        """ Copy card and header images to the blog app's static dir. """
        src = os.path.join(self.blog_dir, archive, slug, '%s.jpg' % jpg)
        if resolution:
            dst = os.path.join(
                self.img_dir, archive, '%s-%d.jpg' % (slug, resolution)
            )
        else:
            dst = os.path.join(self.img_dir, '%s.jpg' % slug)
        changed = False
        try:
            if not filecmp.cmp(src, dst):
                changed = True
        except FileNotFoundError:
            changed = True
        if changed:
            copyfile(src, dst)
            print('Copied %s' % dst)
        return changed

    def _date(self, archive, slug, filename, reverse=False):
        """ Return a date for the file from git log. """
        if archive:
            path = 'blog/%s/%s/%s' % (slug, archive, filename)
        else:
            path = 'blog/%s/%s' % (slug, filename)
        cmd = ['--format=%ad', '--date=raw', '--', path]
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

    def _lede(self, archive, slug):
        """ Return a string for the lede field. """
        path = os.path.join(self.blog_dir, archive, slug, 'lede.md')
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.read()
        return None

    def _title(self, archive, slug):
        """ Return a string for the title field. """
        path = os.path.join(self.blog_dir, archive, slug, 'content.md')
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.readline()[2:]
        return None

    def _create(self, archive, slug, is_published):
        """ Create a new blog entry. """
        first_published = self._date(archive, slug, 'content.md', True)
        last_update = self._date(archive, slug, 'content.md')
        if last_update:
            lede = self._lede(archive, slug)
            title = self._title(archive, slug)
            entry = Entry.objects.create(
                first_published=first_published,
                last_update=last_update,
                lede=lede,
                published=is_published,
                slug=slug,
                title=title,
            )
            self._cp_static(archive, entry.slug, 'header')
            self._cp_static(archive, entry.slug, 'card', 120)
            print('Created', archive, entry.slug)

    def _update(self, entry, archive):
        """ Update an existing blog entry. """
        data = {}
        data['last_update'] = self._date(archive, entry.slug, 'content.md')
        if data['last_update']:
            data['lede'] = self._lede(archive, entry.slug)
            data['title'] = self._title(archive, entry.slug)
        changed = False
        for key, value in data.items():
            if getattr(entry, key) != value:
                setattr(entry, key, value)
                changed = True
        if changed:
            entry.save()
            print('Updated', entry.slug)
        self._cp_static(archive, entry.slug, 'header')
        self._cp_static(archive, entry.slug, 'card', 120)

    def handle(self, *args, **options):
        """ Import blog data. """

        # Gather archive/entry data from the file system.
        entries = {}  # Map entry slug to entry data dict.
        archives = {}  # Map archive slug to archive data dict.
        for root_dir in os.listdir(self.blog_dir):
            meta_file = os.path.join(root_dir, 'meta.py')
            if os.path.isfile(meta_file):
                with open(meta_file) as meta_fd:
                    archives[root_dir] = ast.literal_eval(meta_fd.read())
                sub_dirs = os.listdir(os.path.join(self.blog_dir, root_dir))
                for sub_dir in sub_dirs:
                    if sub_dir in entries:
                        raise Exception('Duplicate entry %s' % sub_dir)
                    entries[sub_dir] = {'archive': root_dir}
            else:
                if root_dir in entries:
                    raise Exception('Duplicate entry %s' % root_dir)
                entries[root_dir] = {'archive': ''}

        # Set entry database action.
        for entry in Entry.objects.all():
            if entry.slug in entries:
                entries[entry.slug]['object'] = entry
                entries[entry.slug]['action'] = 'update'
            else:
                entries[entry.slug] = {'object': entry, 'action': 'delete'}

        # Publish all entries if the db is empty.
        is_published = True
        if entries:
            is_published = False

        # Create, update, delete.
        for slug, entry in entries.items():
            if entry.get('action') == 'update':
                self._update(entry['object'], entry.get('archive'))
            elif entry.get('action') == 'delete':
                entry['object'].delete()
                print('Deleted', entry.slug)
            else:
                self._create(entry.get('archive'), slug, is_published)
