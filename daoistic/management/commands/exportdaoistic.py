""" Management utility to export db tables to markdown. """
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from daoistic.models import Chapter


def _write_chapter(obj, out):
    out.write('# Chapter %d\n\n' % obj.number)
    if obj.title:
        out.write('%s\n\n' % obj.title)
    if obj.published:
        out.write('## Published (yes)\n\n')
    else:
        out.write('## Published\n\n')
    if obj.last_update:
        out.write('%s\n\n' % obj.last_update.strftime("%B %d, %Y"))
    if obj.hanzi:
        out.write('## Hanzi\n\n')
        out.write(obj.hanzi.replace('\r', ''))
        out.write('\n\n')
    if obj.english:
        out.write('## English\n\n')
        out.write(obj.english.replace('\r', ''))
        out.write('\n\n')
    if obj.notes:
        out.write('## Notes\n\n')
        out.write(obj.notes.replace('\r', ''))
        out.write('\n\n')
    print('Exported %d to markdown' % obj.number)

class Command(BaseCommand):
    """ A command to import daoistic db data. """

    help = 'Used to export daoistic db data.'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        """ Export daoistic data. """
        data_file = os.path.join(
            settings.BASE_DIR, 'var', 'daoistic', 'daoistic.md'
        )
        with open(data_file, 'w') as out:
            objs = Chapter.objects.filter(
                book__title='道德經'
            ).order_by('number')
            for obj in objs:
                _write_chapter(obj, out)
