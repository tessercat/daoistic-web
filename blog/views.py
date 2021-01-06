""" Blog views module. """
import os
import string
import markdown
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.formats import date_format
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from common.views import css_file
from common.decorators import cache_public
from unihan.api import unihan_map
from blog.models import Entry


# pylint: disable=too-many-ancestors
@method_decorator(cache_public(60 * 15), name='dispatch')
class BlogView(ListView):
    """ Reverse-chronological view of the last nine entries. """

    model = Entry
    template_name = 'blog/blog.html'

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Daoistic'
        context['css_file'] = css_file()
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.all().order_by('-last_update')[:9]
        else:
            entries = Entry.objects.filter(
                published=True
            ).order_by('-last_update')[:9]
        for entry in entries:
            entry.card_date = 'Last update %s' % date_format(entry.last_update)
            entry.card_img = '%s-120.jpg' % entry.slug
        return entries


class ArchiveIndexView(ListView):
    """ Chronological view of archive dirs and unarchived entries. """
    model = Entry
    template_name = 'blog/archive_index.html'

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Archive'
        context['css_file'] = css_file()
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.all().order_by('first_published')
        else:
            entries = Entry.objects.filter(
                published=True
            ).order_by('first_published')
        for entry in entries:
            card_date = date_format(entry.first_published)
            last_update = date_format(entry.last_update)
            if last_update != card_date:
                card_date = '%s. Last update %s' % (card_date, last_update)
            entry.card_date = card_date
            entry.card_img = '%s-120.jpg' % entry.slug
        return entries


class ArchiveView(TemplateView):
    """ Chronological view of an archive dir's entries. """
    template_name = 'blog/archive.html'

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'A Daoistic page of archived entries'
        context['css_file'] = css_file()
        return context


class EntryView(DetailView):
    """ Blog entry view. """

    model = Entry
    template_name = 'blog/entry.html'

    def get_object(self, queryset=None):
        """ Raise 404 for unpublished entries. """
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.published:
            raise Http404()
        return obj

    # pylint: disable=too-many-locals
    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['page_title'] = obj.title
        context['css_file'] = css_file()
        if self.request.resolver_match.url_name == 'study':
            context['is_study'] = True
        else:
            context['is_study'] = False
        entry_base = os.path.join(
            settings.BASE_DIR, 'var', 'data', 'blog', obj.slug,
        )

        # Entry content.
        content_file = os.path.join(entry_base, 'content.md')
        with open(content_file) as content_fd:
            if context['is_study'] or obj.allow_hanzi:
                content = content_fd.read()
            else:
                content = []
                for line in content_fd.readlines():
                    if line[0] in string.printable:
                        content.append(line)
                content = ''.join(content)
        context['content'] = markdown.markdown(content)

        # Entry notes.
        context['notes'] = ''
        if context['is_study']:
            notes_file = os.path.join(entry_base, 'notes.md')
            if os.path.isfile(notes_file):
                with open(notes_file) as notes_fd:
                    context['notes'] = markdown.markdown(notes_fd.read())

        # Char map for content/notes.
        if context['is_study'] or obj.allow_hanzi:
            chars = content + context['notes']
        else:
            chars = context['notes']
        context['char_map'] = unihan_map(chars)

        # Refs file to list of links, one per line.
        context['ref_links'] = []
        refs_file = os.path.join(entry_base, 'refs.html')
        if os.path.isfile(refs_file):
            with open(refs_file) as refs_fd:
                for ref in refs_fd.readlines():
                    context['ref_links'].append(ref.strip())

        # Static image links.
        context['header_img'] = '%s.jpg' % obj.slug
        context['card_img'] = '%s-120.jpg' % obj.slug
        return context
