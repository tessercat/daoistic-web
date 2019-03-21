""" Management utility to create daoistic book and chapter tables. """
from datetime import date, datetime
import glob
from itertools import islice
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from daoistic.models import Book, Chapter


def _create_book(book_data):
    """ Create a book object and return it. """
    return Book.objects.create(
        title=book_data['title'],
        subtitle=book_data['subtitle'],
    )

def _create_chapters(book_obj, book_data):
    """ Create chapter objects with the book object reference and a list
    of chapter data . """
    batch_size = 50 # SQLite 999 variable limit.
    values = iter(book_data)
    while True:
        batch = list(islice(values, batch_size))
        if not batch:
            break
        objs = []
        for chapter in batch:
            objs.append(Chapter(
                book=book_obj,
                english=chapter.get('english') or '',
                hanzi=chapter.get('hanzi') or '',
                last_update=chapter.get('last_update') or date.today(),
                notes=chapter.get('notes') or '',
                number=chapter['number'],
                published=chapter.get('published') or False,
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
            'english': new_state == 'english',
            'hanzi': new_state == 'hanzi',
            'last_update': new_state == 'last_update',
            'notes': new_state == 'notes',
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
            elif line.startswith('## Published'):
                state = change_state(state, 'last_update')
                chapter_data['published'] = '(yes)' in line
                current_data = []
            elif line.startswith('## English'):
                state = change_state(state, 'english')
                current_data = []
            elif line.startswith('## Hanzi'):
                state = change_state(state, 'hanzi')
                current_data = []
            elif line.startswith('## Notes'):
                state = change_state(state, 'notes')
                current_data = []
            else:
                if True in states.values():
                    current_data.append(line.strip())

        # Add last chapter.
        change_state(state, None)
        if chapter_data:
            book_data.append(chapter_data)

    # Clean up last update data and return.
    for chapter in book_data:
        if 'last_update' in chapter:
            chapter['last_update'] = datetime.strptime(
                chapter['last_update'], '%B %d, %Y',
            ).date()
    return book_data

class Command(BaseCommand):
    """ A command to import daoistic db data. """

    help = 'Used to import daoistic db data.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        """ Import daoistic data. """
        data_dir = os.path.join(settings.BASE_DIR, 'var', 'daoistic')

        # Get and create daoistic.md book/chapter data.
        title_data = {
            'title': '道德經',
            'subtitle': 'Dao De Jing',
        }
        book_obj = _create_book(title_data)
        book_data = _get_book_data(
            os.path.join(data_dir, 'daoistic.md')
        )
        _create_chapters(book_obj, book_data)

        # Get and create ctext book/chapter data.
        for data_glob in glob.glob(os.path.join(data_dir, 'ctext', '*.md')):
            title_data = _get_title_data(
                os.path.join(data_dir, 'ctext', data_glob)
            )
            book_obj = _create_book(title_data)
            book_data = _get_book_data(
                os.path.join(data_dir, 'ctext', data_glob)
            )
            _create_chapters(book_obj, book_data)
