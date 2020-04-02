""" Management utility to import 道德經 chapters. """
import argparse
import ast
from datetime import datetime, timedelta, timezone
import os
from django.conf import settings
from django.core.management.base import BaseCommand
import sh
from book.models import Book, Chapter


class Command(BaseCommand):
    """ A command to import chapter data. """

    help = 'Used to import chapter data.'
    requires_migrations_checks = True
    book_dir = os.path.join(settings.BASE_DIR, 'var', 'book')
    git = sh.git.bake(_cwd=book_dir, _tty_out=False)

    def _filepath(self, chapter, filename):
        """ Return Dao De Jing chapter file path. """
        return os.path.join(
            self.book_dir,
            'daodejing',
            str(chapter).zfill(2),
            filename,
        )

    def _git_log_date(self, chapter, filename):
        """ Return git log datetime for a file. """
        cmd = [
            '-1', '--format=%ad', '--date=raw', '--',
            'daodejing/%s/%s' % (str(chapter).zfill(2), filename),
        ]
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
        raise ValueError('Bad log date')

    def _meta(self, chapter):
        """ Return dict of chapter meta data. """
        with open(self._filepath(chapter, 'meta.py')) as meta_fd:
            return ast.literal_eval(meta_fd.read())

    def _text(self, chapter, filename):
        """ Return string of chapter text. """
        filepath = self._filepath(chapter, filename)
        if os.path.isfile(filepath):
            with open(filepath) as meta_fd:
                return meta_fd.read()
        print('Chapter %d %s not found.' % (chapter, filename))
        return ''

    def add_arguments(self, parser):
        """ Add --chapter arg. Validate a single int or "all". """

        def chapter_type(arg):
            """ Return chapter list. """
            if arg == 'all':
                return range(1, 82)
            try:
                if 1 <= int(arg) <= 81:
                    return [int(arg)]
            except ValueError:
                pass
            raise argparse.ArgumentTypeError('%s is not all or 1-81' % arg)

        parser.add_argument('--chapter', required=True, type=chapter_type)

    def handle(self, *args, **options):
        """ Import chapter data. """

        # The book object.
        book_obj, created = Book.objects.get_or_create(
            title='道德經',
            defaults={
                'title': '道德經',
                'subtitle': 'Dao De Jing',
            },
        )
        if created:
            print('Created Dao De Jing book.')

        # Get chapter object.
        for chapter in options['chapter']:
            meta = self._meta(chapter)
            english = self._text(chapter, 'english.md')
            english_update = self._git_log_date(chapter, 'english.md')
            hanzi = self._text(chapter, 'hanzi.md')
            hanzi_update = self._git_log_date(chapter, 'hanzi.md')
            notes = self._text(chapter, 'notes.md')
            _, created = Chapter.objects.update_or_create(
                number=chapter,
                title=meta['title'],
                published=meta['published'],
                english=english,
                last_english_update=english_update,
                hanzi=hanzi,
                last_hanzi_update=hanzi_update,
                notes=notes,
                defaults={
                    'number': chapter,
                    'book': book_obj,
                    'title': meta['title'],
                    'published': meta['published'],
                    'english': english,
                    'last_english_update': english_update,
                    'hanzi': hanzi,
                    'last_hanzi_update': hanzi_update,
                    'notes': notes,
                },
            )
            if created:
                print('Created Dao De Jing chapter %d.' % chapter)
