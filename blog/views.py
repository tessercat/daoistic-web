""" Blog views module. """
import os
import string
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
import markdown
from blog.models import Entry
from user.decorators import cache_public
from unihan.api import unihan_map


# pylint: disable=too-many-ancestors
@method_decorator(cache_public(60 * 15), name='dispatch')
class EntryListView(ListView):
    """ Entry index grid view. """

    model = Entry
    template_name = 'blog/entries.html'

    # pylint: disable=arguments-differ
    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Blogging the unbloggable'
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.all().order_by('-pk')
        else:
            entries = Entry.objects.filter(
                published=True).order_by('-pk')
        for entry in entries:
            entry.static_img = 'blog/img/%s-128.jpg' % entry.slug
        return entries


@method_decorator(cache_public(60 * 15), name='dispatch')
class EntryDetailView(DetailView):
    """ Blog entry view. """

    model = Entry
    template_name = 'blog/entry.html'

    @staticmethod
    def _stripped(content):
        """ Return content stripped of non-ascii characters. """

    def get_object(self, queryset=None):
        """ Raise 404 for unpublished entries. """
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.published:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['page_title'] = obj.title
        entry_base = os.path.join(
            settings.BASE_DIR, 'var', 'book', 'blog', obj.slug,
        )

        # Entry content. Strip non-printable for unauthenticated requests.
        content_file = os.path.join(entry_base, 'content.md')
        with open(content_file) as content_fd:
            content = content_fd.read()
        if not self.request.user.is_authenticated and not obj.allow_hanzi:
            printable = set(string.printable)
            content = ''.join(filter(lambda char: char in printable, content))
        context['content'] = markdown.markdown(content)

        # Entry notes.
        context['notes'] = ''
        notes_file = os.path.join(entry_base, 'notes.md')
        if os.path.isfile(notes_file):
            with open(notes_file) as notes_fd:
                context['notes'] = markdown.markdown(notes_fd.read())

        # Char map for content/notes.
        if self.request.user.is_authenticated or obj.allow_hanzi:
            chars = content + context['notes']
        else:
            chars = context['notes']
        context['char_map'] = unihan_map(chars)

        # Refs file to list of links, one per line.
        context['refs'] = []
        refs_file = os.path.join(entry_base, 'refs.html')
        if os.path.isfile(refs_file):
            with open(refs_file) as refs_fd:
                for ref in refs_fd.readlines():
                    context['refs'].append(ref.strip())

        # Static image links.
        context['static_img'] = 'blog/img/%s.jpg' % obj.slug

        return context
