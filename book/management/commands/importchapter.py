""" Management utility to import 道德經 chapters. """
import argparse
import ast
from datetime import date
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

    def _date(self, chapter, filename):
        """ Return git log datetime for a file. """
        cmd = [
            '-1', '--format=%ad', '--date=raw', '--',
            'daodejing/%s/%s' % (str(chapter).zfill(2), filename),
        ]
        result = self.git.log(cmd)
        if result:
            parts = result.stdout.decode().strip().split()
            return date.fromtimestamp(int(parts[0]))
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

        # Update or create chapter objects.
        for chapter in options['chapter']:
            data = self._meta(chapter)
            data['english'] = self._text(chapter, 'english.md')
            data['last_english_update'] = self._date(chapter, 'english.md')
            data['hanzi'] = self._text(chapter, 'hanzi.md')
            data['last_hanzi_update'] = self._date(chapter, 'hanzi.md')
            data['notes'] = self._text(chapter, 'notes.md')
            try:
                chapter_obj = Chapter.objects.get(
                    book__title='道德經',
                    number=chapter,
                )
                changed = False
                for key, value in data.items():
                    if (
                            hasattr(chapter_obj, key)
                            and getattr(chapter_obj, key) != value):
                        setattr(chapter_obj, key, value)
                        changed = True
                if changed:
                    chapter_obj.save()
                    print('Changed Dao De Jing chapter %d.' % chapter)
            except Chapter.DoesNotExist:
                data['book'] = book_obj
                data['number'] = chapter
                chapter_obj = Chapter(**data)
                chapter_obj.save()
                print('Created Dao De Jing chapter %d.' % chapter)
