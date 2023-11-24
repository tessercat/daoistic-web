""" Management utility to import entries from markdown. """
import ast
import filecmp
import shutil
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_date
from entry.models import Archive, Entry


class Command(BaseCommand):
    """ A command to import archive and entry data to the project db. """

    help = 'Used to import and update archive and entry data.'
    requires_migrations_checks = True
    data_dir = settings.BASE_DIR / 'var' / 'data'
    entries_dir = data_dir / 'entries'
    img_dir = settings.BASE_DIR / 'entry' / 'static' / 'entry' / 'img'

    def _cp_static(self, entry_slug, src_type, resolution=None):
        """ Copy image to the entry app's static dir. """
        src = self.entries_dir / entry_slug / f'{src_type}.jpg'
        if resolution:
            dst = self.img_dir / f'{entry_slug}-{resolution}.jpg'
        else:
            dst = self.img_dir / f'{entry_slug}.jpg'
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
            path = self.img_dir / f'{entry_slug}-{resolution}'
        else:
            path = self.img_dir / f'{entry_slug}.jpg'
        try:
            os.remove(path)
            print('Removed', path)
        except OSError:
            print('Error removing', path)

    def _get_title(self, entry_slug):
        """ Return a string for the title field. """
        path = self.entries_dir / entry_slug / 'entry.md'
        if os.path.isfile(path):
            with open(path) as path_fd:
                return path_fd.readline()[2:].strip()
        return None

    def _update_archive(self, archive_obj, title, subtitle, image):
        changed = False
        data = {
            'title': title,
            'subtitle': subtitle,
            'image': image
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
        """ Create a new entry. """
        title = self._get_title(entry_slug)
        last_update = parse_date(entry_data['last_update'])
        Entry.objects.create(
            archive=entry_data['archive'],
            copyright_year=entry_data['copyright'],
            last_update=last_update,
            entry_type=entry_data.get('entry_type', 'study'),
            lede=entry_data['lede'],
            published=entry_data.get('published', False),
            slug=entry_slug,
            title=title,
            weight=entry_data['weight']
        )
        self._cp_static(entry_slug, 'header')
        self._cp_static(entry_slug, 'card', 120)
        print('Created entry', entry_slug)

    def _update_entry(self, entry_data):
        """ Update an existing entry. """
        entry_obj = entry_data['object']
        entry_data['title'] = self._get_title(entry_obj.slug)
        entry_data['last_update'] = parse_date(entry_data['last_update'])
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
        """ Import entry data. """

        # Read archive config.
        with open(self.entries_dir / 'meta.py', encoding='utf-8') as cfg_fd:
            archive_map = ast.literal_eval(cfg_fd.read())['archives']

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
                    archive_data['subtitle'],
                    archive_data['image']
                )
            elif archive_data.get('action') == 'delete':
                archive_data['object'].delete()
                archive_data['object'] = None
                print('Deleted archive', archive_slug)
            else:
                obj = Archive.objects.create(
                    slug=archive_slug,
                    title=archive_data['title'],
                    subtitle=archive_data['subtitle'],
                    image=archive_data['image']
                )
                archive_data['object'] = obj
                print('Created archive', archive_slug)

        # Map entry slug to entry data dict.
        entry_map = {}
        for dir_entry in os.scandir(self.entries_dir):
            if os.path.isdir(dir_entry):
                entry_file = Path(dir_entry) / 'meta.py'
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
