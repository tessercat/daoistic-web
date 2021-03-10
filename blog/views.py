""" Blog views module. """
import os
import markdown
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.formats import date_format
from django.views.generic import DetailView, ListView
from common.decorators import cache_public
from unihan.views import is_unihan, unihan_map
from blog.models import Archive, Entry


def _set_entry_date(entry):
    """ Set entry_date on entry. """
    entry_date = date_format(entry.first_published)
    last_update = date_format(entry.last_update)
    if last_update != entry_date:
        entry_date = '%s. Last update %s.' % (entry_date, last_update)
    entry.entry_date = entry_date


@method_decorator(cache_public(60 * 15), name='dispatch')
class BlogList(ListView):
    """ Reverse-chronological view of the last nine entries. """
    # pylint: disable=too-many-ancestors
    model = Entry
    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Daoistic'
        context['common_css'] = settings.COMMON_CSS
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


@method_decorator(cache_public(60 * 15), name='dispatch')
class ArchiveIndex(ListView):
    """ List of archive cards. """
    # pylint: disable=too-many-ancestors
    model = Entry
    template_name = 'blog/archive-index.html'

    def get_context_data(self, **kwargs):
        """ Add archive card data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Daoistic archive'
        context['common_css'] = settings.COMMON_CSS
        context['archive_objects'] = []
        for obj in Archive.objects.all().order_by('slug'):
            if self.request.user.is_authenticated:
                entry = obj.entry_set.all().order_by(
                    'weight', 'first_published'
                ).first()
            else:
                entry = obj.entry_set.filter(
                    published=True
                ).order_by('weight', 'first_published').first()
            if entry:
                obj.card_img = '%s-120.jpg' % entry.slug
                context['archive_objects'].append(obj)
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.filter(
                archive__isnull=True,
            ).order_by('weight', 'first_published')
        else:
            entries = Entry.objects.filter(
                archive__isnull=True,
                published=True
            ).order_by('weight', 'first_published')
        for entry in entries:
            entry.card_img = '%s-120.jpg' % entry.slug
        return entries


@method_decorator(cache_public(60 * 15), name='dispatch')
class ArchiveList(ListView):
    """ List of entry cards. """
    # pylint: disable=too-many-ancestors
    archive = None
    model = Entry
    template_name = 'blog/archive-list.html'

    def _get_archive(self):
        """ Return the request's archive or raise 404. """
        if (
                self.request.resolver_match
                and hasattr(self.request.resolver_match, 'kwargs')):
            slug = self.request.resolver_match.kwargs.get('slug')
            if slug:
                return get_object_or_404(Archive, slug=slug)
        raise Http404()

    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.archive.title
        context['common_css'] = settings.COMMON_CSS
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        self.archive = self._get_archive()
        if self.request.user.is_authenticated:
            entries = Entry.objects.filter(
                archive=self.archive,
            ).order_by('weight', 'first_published')
        else:
            entries = Entry.objects.filter(
                archive=self.archive,
                published=True
            ).order_by('weight', 'first_published')
        for entry in entries:
            entry.card_img = '%s-120.jpg' % entry.slug
        return entries


@method_decorator(cache_public(60 * 15), name='dispatch')
class EntryDetails(DetailView):
    """ Blog entry view. """
    model = Entry
    template_name = 'blog/entry.html'

    def get_object(self, queryset=None):
        """ Raise 404 for unpublished entries. """
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.published:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['page_title'] = obj.title
        context['common_css'] = settings.COMMON_CSS
        context['common_js'] = settings.COMMON_JS
        _set_entry_date(obj)
        entry_dir = os.path.join(
            settings.BASE_DIR, 'var', 'data', 'blog', obj.slug,
        )

        # Set context state variables.
        char_data = ''
        strip_content = True
        publish_notes = False
        publish_vocabulary = False
        context['study_link'] = True
        if obj.entry_type != 'study':
            strip_content = False
            publish_vocabulary = True
            context['study_link'] = False
        if self.request.resolver_match.url_name == 'blog-entry-study':
            if obj.entry_type != 'study':
                raise Http404()
            strip_content = False
            publish_notes = True
            publish_vocabulary = True
            context['study_link'] = False
            context['plain_link'] = True

        # Read notes.
        if publish_notes:
            notes_file = os.path.join(entry_dir, 'notes.md')
            if os.path.isfile(notes_file):
                with open(notes_file) as notes_fd:
                    notes = notes_fd.read()
                    if publish_vocabulary:
                        char_data += notes
                    context['notes'] = markdown.markdown(notes)

        # Read content.
        content_file = os.path.join(entry_dir, 'content.md')
        lines = []
        with open(content_file) as content_fd:
            for line in content_fd.readlines():
                if strip_content and is_unihan(line[0]):
                    continue
                lines.append(line)
        content = ''.join(lines[2:])  # Remove title lines.
        context['content'] = markdown.markdown(content)
        if publish_vocabulary and not strip_content:
            char_data = content + char_data

        # Process the character map.
        context['unihan_map'] = None
        if publish_vocabulary:
            if self.request.user.is_authenticated:
                context['unihan_map'] = unihan_map(char_data, False, 'search')
            else:
                context['unihan_map'] = unihan_map(char_data, False)

        # Refs file to list of links, one per line.
        context['ref_links'] = []
        refs_file = os.path.join(entry_dir, 'refs.html')
        if os.path.isfile(refs_file):
            with open(refs_file) as refs_fd:
                for ref in refs_fd.readlines():
                    context['ref_links'].append(ref.strip())

        # Static image links.
        context['header_img'] = '%s.jpg' % obj.slug
        context['card_img'] = '%s-120.jpg' % obj.slug
        return context
