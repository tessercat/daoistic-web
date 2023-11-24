""" Entry app views module. """
from datetime import datetime
import os
import markdown
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.formats import date_format
from django.views.generic import DetailView, ListView
from common.decorators import cache_public
from unihan.views import is_unihan, unihan_map
from entry.models import Archive, Entry


@method_decorator(cache_public(60 * 15), name='dispatch')
class BlogIndex(ListView):
    """ Reverse-chronological view of the last nine entries. """
    # pylint: disable=too-many-ancestors
    model = Entry
    template_name = 'entry/blog-index.html'

    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Daoistic'
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.filter(
                entry_type__startswith='study'
            ).order_by('-last_update', '-pk')[:9]
        else:
            entries = Entry.objects.filter(
                entry_type__startswith='study',
                published=True
            ).order_by('-last_update', '-pk')[:9]
        for entry in entries:
            entry.card_date = f'Last update {date_format(entry.last_update)}'
            entry.card_img = f'{entry.slug}-120.jpg'
        return entries


@method_decorator(cache_public(60 * 15), name='__call__')
class BlogFeed(Feed):
    """ Blog RSS feed. """
    title = "Daoistic"
    link = "/"
    description = "By last update"

    def items(self):
        """ Return published items ordered by last update. """
        return Entry.objects.filter(
            published=True,
            entry_type__startswith='study'
        ).order_by('-last_update', '-pk')[:9]

    def item_title(self, item):
        """ Return entry title. """
        return item.title

    def item_description(self, item):
        """ Return entry lede. """
        return item.lede

    def item_link(self, item):
        """ Return entry link. """
        return reverse('entry-plain', args=[item.slug])

    def item_pubdate(self, item):
        """ Return item last_update datetime. """
        return datetime.combine(item.last_update, datetime.min.time())


@method_decorator(cache_public(60 * 15), name='dispatch')
class ArchiveIndex(ListView):
    """ List of archive cards. """
    # pylint: disable=too-many-ancestors
    model = Archive
    template_name = 'entry/archive-index.html'

    def get_context_data(self, **kwargs):
        """ Add archive card data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Daoistic'
        return context

    def get_queryset(self):
        """ Return objects for the grid. """
        archives = Archive.objects.all().order_by('slug')
        for archive in archives:
            archive.card_img = f'{archive.image}-120.jpg'
        return archives


@method_decorator(cache_public(60 * 15), name='dispatch')
class ArchiveList(ListView):
    """ List of entry cards. """
    # pylint: disable=too-many-ancestors
    archive = None
    model = Entry
    template_name = 'entry/archive-list.html'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if slug:
            if slug == 'various':
                route = request.resolver_match.route.split('/')[:-1] + ['tong']
                redirect_url = '/' + '/'.join(route)
                return HttpResponseRedirect(redirect_url)
            self.archive = get_object_or_404(Archive, slug=slug)
            return super().get(request, *args, **kwargs)
        raise Http404()

    def get_context_data(self, **kwargs):
        """ Add entry data to the template context. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.archive.title
        return context

    def get_queryset(self):
        """ Return entries for the grid. """
        if self.request.user.is_authenticated:
            entries = Entry.objects.filter(
                archive=self.archive,
            ).order_by('weight')
        else:
            entries = Entry.objects.filter(
                archive=self.archive,
                published=True
            ).order_by('weight')
        for entry in entries:
            entry.card_img = f'{entry.slug}-120.jpg'
        return entries


@method_decorator(cache_public(60 * 15), name='dispatch')
class EntryDetails(DetailView):
    """ Entry details view. """
    model = Entry
    template_name = 'entry/entry.html'

    def get_object(self, queryset=None):
        """ Raise 404 for unpublished entries. """
        obj = super().get_object()
        if not obj.published and not self.request.user.is_authenticated:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['page_title'] = obj.title
        context['entry_date'] = f'Last update {date_format(obj.last_update)}.'
        entry_dir = settings.BASE_DIR / 'var' / 'data' / 'entries' / obj.slug

        # Set context state variables.
        char_data = ''
        strip_entry = True
        publish_notes = False
        publish_vocabulary = False
        context['is_plain'] = True
        if obj.entry_type != 'study':
            strip_entry = False
            publish_vocabulary = True
            context['is_plain'] = False
        if self.request.resolver_match.url_name == 'entry-study':
            if obj.entry_type != 'study':
                raise Http404()
            strip_entry = False
            publish_notes = True
            publish_vocabulary = True
            context['is_plain'] = False
            context['is_study'] = True
            context['page_title'] += ' 文'

        # Read notes.
        if publish_notes:
            notes_file = os.path.join(entry_dir, 'notes.md')
            if os.path.isfile(notes_file):
                with open(notes_file, encoding='utf8') as notes_fd:
                    notes = notes_fd.read()
                    if publish_vocabulary:
                        char_data += notes
                    context['notes'] = markdown.markdown(notes)

        # Read entry.
        entry_file = os.path.join(entry_dir, 'entry.md')
        lines = []
        with open(entry_file, encoding='utf8') as entry_fd:
            for line in entry_fd.readlines():
                if strip_entry and is_unihan(line[0]):
                    continue
                lines.append(line)
        entry = ''.join(lines[2:])  # Remove title lines.
        context['entry'] = markdown.markdown(entry)
        if publish_vocabulary and not strip_entry:
            char_data = entry + char_data

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
            with open(refs_file, encoding='utf8') as refs_fd:
                for ref in refs_fd.readlines():
                    context['ref_links'].append(ref.strip())

        # Static image links.
        context['header_img'] = f'{obj.slug}.jpg'
        context['card_img'] = f'{obj.slug}-120.jpg'
        return context
