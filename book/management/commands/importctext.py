""" Management utility to create book and chapter tables for ctext data. """
import glob
from itertools import islice
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from book.models import Book, Chapter


def _create_chapters(book_obj, book_data):
    """ Create chapter objects from the book object and chapter data list. """
    batch_size = 50  # SQLite 999 variable limit.
    values = iter(book_data)
    while True:
        batch = list(islice(values, batch_size))
        if not batch:
            break
        objs = []
        for chapter in batch:
            objs.append(Chapter(
                book=book_obj,
                english='',
                hanzi=chapter.get('hanzi') or '',
                notes='',
                number=chapter['number'],
                published=False,
                publish_notes=False,
                title=chapter.get('title') or '',
            ))
        Chapter.objects.bulk_create(objs, batch_size)


def _get_title_data(data_file):
    """ Extract and return title/subtitle data. """

    # Set initial states.
    title = None
    subtitle = None
    in_main = False
    in_subtitle = False

    # Run lines through state machine.
    with open(data_file) as book_fd:
        for line in book_fd.readlines():

            # Stop condition.
            if title and subtitle:
                break

            # Set states.
            if line.strip() == '- type: main':
                in_main = True
                in_subtitle = False
                continue
            if line.strip() == '- type: subtitle':
                in_subtitle = True
                in_main = False
                continue

            # State actions.
            if in_main and line.strip().startswith('text:'):
                title = line.split(':')[1].strip()
            if in_subtitle and line.strip().startswith('text:'):
                subtitle = line.split(':')[1].strip()

    return {
        'title': title,
        'subtitle': subtitle,
    }


def _get_book_data(data_file):
    """ Extract and return book data. """

    # Init chapter state data.
    states = {}
    current_data = []
    chapter_data = {}

    def change_state(current_state=None, new_state=None):
        """ Set new state, store captured data. """
        if current_state:
            line_data = '\r\n'.join(current_data).strip()
            if line_data:
                chapter_data[current_state] = line_data
        states.update({
            'hanzi': new_state == 'hanzi',
            'title': new_state == 'title',
        })
        return new_state

    # Run state machine to collect book data.
    book_data = []
    state = change_state()
    with open(data_file) as book_fd:
        lines = book_fd.readlines()
        for line in lines:
            if line.startswith('# Chapter'):
                state = change_state(state, 'title')
                if chapter_data:
                    book_data.append(chapter_data)
                chapter_data = {'number': int(line.strip().split()[-1])}
                current_data = []
            elif line.startswith('## Hanzi'):
                state = change_state(state, 'hanzi')
                current_data = []
            else:
                if True in states.values():
                    current_data.append(line.strip())

        # Add last chapter.
        change_state(state, None)
        if chapter_data:
            book_data.append(chapter_data)

    return book_data


class Command(BaseCommand):
    """ A command to import ctext book data. """

    help = 'Used to import ctext book data.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        """ Get and create ctext book/chapter data. """
        data_dir = os.path.join(settings.BASE_DIR, 'var', 'book')
        for data_glob in glob.glob(os.path.join(data_dir, 'ctext', '*.md')):
            if data_glob.endswith('README.md'):
                continue
            title_data = _get_title_data(
                os.path.join(data_dir, 'ctext', data_glob)
            )
            book_data = _get_book_data(
                os.path.join(data_dir, 'ctext', data_glob)
            )
            book_obj = Book.objects.create(
                title=title_data['title'],
                subtitle=title_data['subtitle'],
            )
            _create_chapters(book_obj, book_data)
