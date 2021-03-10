""" Management utility to import blog from markdown. """
import ast
from datetime import date
import filecmp
import shutil
import os
from django.core.management.base import BaseCommand
from django.conf import settings
import sh
from blog.models import Archive, Entry


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

    def _cp_static(self, entry_slug, src_type, resolution=None):
        """ Copy image to the blog app's static dir. """
        src = os.path.join(
            self.blog_dir, entry_slug, '%s.jpg' % src_type
        )
        if resolution:
            dst = os.path.join(
                self.img_dir, '%s-%d.jpg' % (entry_slug, resolution)
            )
        else:
            dst = os.path.join(self.img_dir, '%s.jpg' % entry_slug)
        changed = False
        try:
            if not filecmp.cmp(src, dst):
                changed = True
        except FileNotFoundError:
            changed = True
        if changed:
            try:
                shutil.copyfile(src, dst)
                print('Copied', dst)
            except FileNotFoundError:
                print('No', src_type, entry_slug)
        return changed

    def _rm_static(self, entry_slug, resolution=None):
        """ Remove image from the app's static dir. """
        if resolution:
            path = os.path.join(
                self.img_dir, '%s-%d.jpg' % (entry_slug, resolution)
            )
        else:
            path = os.path.join(self.img_dir, '%s.jpg' % entry_slug)
        try:
            os.remove(path)
            print('Removed', path)
        except OSError:
            print('Error removing', path)

    def _git_date(self, entry_slug, filename, first=False):
        """ Return a date for the file from git log. """
        path = 'blog/%s/%s' % (entry_slug, filename)
        cmd = ['--format=%ad', '--date=raw', '--follow', path]
        result = self.git.log(cmd)
        lines = result.stdout.decode().splitlines()
        if first:
            logdate = lines[-1]
        else:
            logdate = lines[0]
        parts = logdate.strip().split()
        return date.fromtimestamp(int(parts[0]))

    def _title(self, entry_slug):
        """ Return a string for the title field. """
        path = os.path.join(self.blog_dir, entry_slug, 'content.md')
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.readline()[2:].strip()
        return None

    def _update_archive(self, archive_obj, title, subtitle):
        changed = False
        data = {
            'title': title,
            'subtitle': subtitle
        }
        for key, new_value in data.items():
            try:
                old_value = getattr(archive_obj, key)
            except AttributeError:
                continue
            if old_value != new_value:
                setattr(archive_obj, key, new_value)
                changed = True
        if changed:
            archive_obj.save()
            print('Updated archive', archive_obj.slug)

    def _create_entry(self, entry_slug, entry_data):
        """ Create a new blog entry. """
        title = self._title(entry_slug)
        first_published = self._git_date(entry_slug, 'content.md', True)
        last_update = self._git_date(entry_slug, 'content.md')
        Entry.objects.create(
            archive=entry_data.get('archive', None),
            first_published=first_published,
            last_update=last_update,
            lede=entry_data['lede'],
            published=entry_data.get('is_published', False),
            slug=entry_slug,
            title=title,
            weight=entry_data.get('weight', 0)
        )
        self._cp_static(entry_slug, 'header')
        self._cp_static(entry_slug, 'card', 120)
        print('Created entry', entry_slug)

    def _update_entry(self, entry_data):
        """ Update an existing blog entry. """
        entry_obj = entry_data['object']
        entry_data['title'] = self._title(entry_obj.slug)
        entry_data['first_published'] = self._git_date(
            entry_obj.slug, 'content.md', True
        )
        entry_data['last_update'] = self._git_date(
            entry_obj.slug, 'content.md'
        )
        changed = False
        for key, new_value in entry_data.items():
            try:
                old_value = getattr(entry_obj, key)
            except AttributeError:
                continue
            if old_value != new_value:
                setattr(entry_obj, key, new_value)
                changed = True
        if changed:
            entry_obj.save()
            print('Updated entry', entry_obj.slug)
        self._cp_static(entry_obj.slug, 'header')
        self._cp_static(entry_obj.slug, 'card', 120)

    def handle(self, *args, **options):
        """ Import blog data. """

        # Read blog config.
        blog_config = {}
        blog_file = os.path.join(self.blog_dir, 'meta.py')
        if os.path.isfile(blog_file):
            with open(blog_file) as blog_fd:
                blog_config = ast.literal_eval(blog_fd.read())

        # Map archive slug to archive data dict.
        archive_map = blog_config.get('archives', {})

        # Process archive map/objects.
        for obj in Archive.objects.all():
            if obj.slug in archive_map:
                archive_map[obj.slug]['object'] = obj
                archive_map[obj.slug]['action'] = 'update'
            else:
                archive_map[obj.slug] = {'object': obj, 'action': 'delete'}

        # Archive CRUD.
        for archive_slug, archive_data in archive_map.items():
            if archive_data.get('action') == 'update':
                self._update_archive(
                    archive_map[archive_slug]['object'],
                    archive_data['title'],
                    archive_data['subtitle']
                )
            elif archive_data.get('action') == 'delete':
                archive_data['object'].delete()
                archive_data['object'] = None
                print('Deleted archive', archive_slug)
            else:
                obj = Archive.objects.create(
                    slug=archive_slug,
                    title=archive_data['title'],
                    subtitle=archive_data['subtitle']
                )
                archive_data['object'] = obj
                print('Created archive', archive_slug)

        # Map entry slug to entry data dict.
        entry_map = {}
        for dir_entry in os.scandir(self.blog_dir):
            if os.path.isdir(dir_entry):
                entry_file = os.path.join(dir_entry, 'meta.py')
                if os.path.isfile(entry_file):
                    with open(entry_file) as entry_fd:
                        entry_config = ast.literal_eval(entry_fd.read())
                    entry_map[dir_entry.name] = entry_config

        # Process entry map/objects.
        for entry_obj in Entry.objects.all():
            if entry_obj.slug in entry_map:
                entry_map[entry_obj.slug]['object'] = entry_obj
                entry_map[entry_obj.slug]['action'] = 'update'
            else:
                entry_map[entry_obj.slug] = {
                    'object': entry_obj, 'action': 'delete'
                }

        # Entry CRUD.
        for entry_slug, entry_data in entry_map.items():
            archive_slug = entry_map[entry_slug].get('archive')
            if archive_slug:
                archive_obj = archive_map[archive_slug]['object']
                entry_map[entry_slug]['archive'] = archive_obj
            else:
                entry_map[entry_slug]['archive'] = None
            if entry_data.get('action') == 'update':
                self._update_entry(entry_data)
            elif entry_data.get('action') == 'delete':
                entry_data['object'].delete()
                print('Deleted entry', entry_slug)
                self._rm_static(entry_slug)
                self._rm_static(entry_slug, 120)
            else:
                self._create_entry(entry_slug, entry_data)
