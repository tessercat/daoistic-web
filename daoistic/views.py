""" Daoistic app views module. """
import os
import re
import markdown
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.utils.html import linebreaks
from django.utils.text import normalize_newlines
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView
from daoistic.decorators import cache_public
from daoistic.models import Book, Chapter
from unihan.models import UnihanCharacter
from unihan.tools import get_char_map


# Map to strip hanzi punctuation.
HANZI_TMAP = dict.fromkeys(map(ord, '，。？'), None)
MAX_SEARCH_CHARS = 2
DDJ_TITLES = ('道德經', '郭店', '馬王堆甲', '馬王堆乙', '河上公', '王弼')

def _chapter_range(page):
    """ Return the poems to display on a page, from low to high. """
    if 1 <= page <= 9:
        low = ((page - 1) * 9) + 1
        high = page * 9
    else:
        raise Http404()
    return low, high

@method_decorator(cache_public(60 * 15), name='dispatch')
class AboutTemplateView(TemplateView):
    """ About-this-site view. """

    template_name = 'daoistic/about.html'

    def get_context_data(self, **kwargs):
        """ Insert about data into index template. """
        context = super().get_context_data(**kwargs)
        context['brand_href'] = '/'
        context['brand_title'] = 'Home'
        about = os.path.join(
            settings.BASE_DIR, 'var', 'daoistic', 'about.md',
        )
        with open(about) as about_fd:
            context['about'] = markdown.markdown(about_fd.read())
        return context

@method_decorator(cache_public(60 * 15), name='dispatch')
class ComparisonView(TemplateView):
    """ Compare versions of the Daodejing side-by-side. """

    template_name = 'daoistic/comparison.html'

    def _get_chapter_list(self):
        """ Return an ordered list of chapters. """
        if not self.request.user.is_authenticated:
            raise Http404() # Unauth'd users have no access.
        if not 1 <= self.kwargs['chapter'] <= 81:
            raise Http404() # Chapter range check.

        # Order chapters by book title.
        chapters = Chapter.objects.filter(
            number=self.kwargs['chapter'],
        )
        books_map = {}
        for chapter in chapters:
            books_map[chapter.book.title] = chapter
        chapter_list = []
        for title in DDJ_TITLES:
            if title in books_map:
                chapter_list.append(books_map[title])
        return chapter_list

    def get_context_data(self, **kwargs):
        """ Insert comparison data. """
        context = super().get_context_data(**kwargs)
        context['chapter_number'] = self.kwargs['chapter']
        context['chapter_list'] = self._get_chapter_list()
        context['brand_href'] = '/'
        context['brand_title'] = 'Home'
        context['poems_href'] = '/poems/chapter/%d' % self.kwargs['chapter']
        context['poems_title'] = 'Poems chapter %d' % self.kwargs['chapter']
        context['studies_href'] = '/studies/chapter/%d' % self.kwargs['chapter']
        context['studies_title'] = 'Studies chapter %d' % self.kwargs['chapter']
        hz_data = set()
        for chapter in context['chapter_list']:
            hz_data.update([hz for hz in chapter.hanzi])
        context['char_map'] = get_char_map(''.join(hz_data))
        return context

class NavJsonView(TemplateView):
    """ Previous/next nav view. """

    def _get_next(self, current):
        """ Return the next chapter number. """

        # Allow auth users to see unpublished chapters.
        if self.request.user.is_authenticated:
            return ((current - 1) + 1) % 81 + 1

        # Get the next in sequence.
        chapter = Chapter.objects.filter(
            book__title='道德經',
            number__gt=current,
            published=True,
        ).order_by('number').first()
        if chapter:
            return chapter.number

        # Wrap, search up from the bottom.
        chapter = Chapter.objects.filter(
            book__title='道德經',
            number__gt=0,
            published=True,
        ).order_by('number').first()
        if chapter:
            return chapter.number

        # Found nothing.
        raise ValidationError('Bad nav request')

    def _get_previous(self, current):
        """ Return the previous chapter number. """

        # Allow auth users to see unpublished chapters.
        if self.request.user.is_authenticated:
            return ((current - 1) + 81 - 1) % 81 + 1

        # Get the previous in sequence.
        chapter = Chapter.objects.filter(
            book__title='道德經',
            number__lt=current,
            published=True,
        ).order_by('number').last()
        if chapter:
            return chapter.number

        # Wrap, search down from the top.
        chapter = Chapter.objects.filter(
            book__title='道德經',
            number__lt=82,
            published=True,
        ).order_by('number').last()
        if chapter:
            return chapter.number

        # Found nothing.
        raise ValidationError('Bad nav request')

    def render_to_response(self, context, **response_kwargs):
        """ Render new nav URL as a JSON response. """
        if context['direction'] == 'next':
            nav_to = self._get_next(context['current'])
        elif context['direction'] == 'previous':
            nav_to = self._get_previous(context['current'])
        else:
            raise ValidationError('Bad nav direction')
        return JsonResponse(
            {'navTo': nav_to},
            **response_kwargs
        )

@method_decorator(cache_public(60 * 15), name='dispatch')
class PoemDetailView(DetailView):
    """ English-only chapter view. """

    model = Chapter
    template_name = 'daoistic/poem_details.html'

    def get_context_data(self, **kwargs):
        """ Insert poem chapter data into index template. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Chapter %d | %s' % (
            self.kwargs['chapter'], self.object.title,
        )
        page_number = ((self.kwargs['chapter'] - 1) / 9) + 1
        if page_number == 1:
            context['brand_href'] = '/poems'
            context['brand_title'] = 'Poems home'
            context['poems_href'] = '/poems'
            context['poems_title'] = 'Poems home'
            context['studies_href'] = '/studies/chapter/%d' % self.object.number
            context['studies_title'] = 'Studies chapter %d' % self.object.number
        else:
            context['brand_href'] = '/poems/page/%d' % page_number
            context['brand_title'] = 'Poems page %d' % page_number
            context['poems_href'] = '/poems/page/%d' % page_number
            context['poems_title'] = 'Poems page %d' % page_number
            context['studies_href'] = '/studies/chapter/%d' % self.object.number
            context['studies_title'] = 'Studies chapter %d' % self.object.number
        return context

    def get_object(self, queryset=None):
        """ Return the chapter object to detail. """

        # Fetch/validate requested chapter.
        if 'chapter' not in self.kwargs:
            self.kwargs['chapter'] = 1
        try:
            filter_args = [Q(book__title='道德經')]
            if not self.request.user.is_authenticated:
                filter_args.append(Q(published=True))
            chapter = Chapter.objects.get(
                number=self.kwargs['chapter'],
                *filter_args,
            )
        except Chapter.DoesNotExist:
            raise Http404()

        # Add view-specific data to the object and return it.
        chapter.english_html = linebreaks(chapter.english)
        chapter.copyright_year = chapter.last_update.year
        return chapter

@method_decorator(cache_public(60 * 15), name='dispatch')
class PoemListView(ListView):
    """ Poem index grid view. """

    model = Chapter
    template_name = 'daoistic/poem_list.html'

    @classmethod
    def _add_summary(cls, chapter):
        """ Add a summary field to a chapter. """
        summary = chapter.english.split('\n', 1)[0].strip()
        if summary.endswith(','):
            summary = summary[:-1]
        if not summary.endswith('.'):
            summary += '.'
        chapter.summary = summary

    def get_context_data(self, *, object_list=None, **kwargs):
        """ Insert poem page data into index template. """
        context = super().get_context_data(**kwargs)
        context['page_number'] = self.kwargs['page']
        context['page_title'] = 'Chapters %d-%d' % self.kwargs['chapters']
        context['brand_href'] = '/poems'
        context['brand_title'] = 'Poems home'
        context['poems_href'] = '/poems'
        context['poems_title'] = 'Poems home'
        if self.kwargs['page'] == 1:
            context['studies_href'] = '/studies'
            context['studies_title'] = 'Studies home'
        else:
            context['studies_href'] = '/studies/page/%d' % self.kwargs['page']
            context['studies_title'] = 'Studies page %d' % self.kwargs['page']
        return context

    def get_queryset(self):
        """ Return chapters for the grid. """
        if 'page'  not in self.kwargs:
            self.kwargs['page'] = 1
        self.kwargs['chapters'] = _chapter_range(self.kwargs['page'])
        chapters = Chapter.objects.filter(
            book__title='道德經',
            number__range=self.kwargs['chapters'],
            published=True,
        )
        for chapter in chapters:
            PoemListView._add_summary(chapter)
        return chapters

@method_decorator(cache_public(60 * 15), name='dispatch')
class SearchBooksView(TemplateView):
    """ A view of the books containing the search characters. """

    template_name = 'daoistic/search_books.html'

    def _get_books(self):
        """ Return books for the grid. """

        # Request validation.
        if not self.request.user.is_authenticated:
            raise Http404() # Unauth'd users can't search books.
        for char in self.kwargs['chars']:
            try:
                UnihanCharacter.objects.get(pk=ord(char))
            except UnihanCharacter.DoesNotExist:
                raise Http404() # A search character doesn't exist.

        # A list of dicts of chapters containing all search chars.
        chapters = Chapter.objects.filter(
            *[Q(hanzi__contains=char) for char in self.kwargs['chars']],
        ).values(
            'book__title',
            'book__subtitle',
        )

        # A dict of book title to chapter count.
        books_map = {}
        for chapter in chapters:
            if chapter['book__title'] in books_map:
                books_map[chapter['book__title']] += 1
            else:
                books_map[chapter['book__title']] = 1

        # An ordered list of book title and chapter count.
        books = []
        for title in DDJ_TITLES:
            if title in books_map:
                books.append((title, books_map[title]))
        return books

    def get_context_data(self, **kwargs):
        """ Insert study page data into index template. """
        context = super().get_context_data(**kwargs)
        context['brand_href'] = '/poems'
        context['brand_title'] = 'Poems home'
        context['books'] = self._get_books()
        return context

@method_decorator(cache_public(60 * 15), name='dispatch')
class SearchChaptersView(ListView):
    """ A view of the chapters of a particular book that contain all
    search characters. """

    model = Chapter
    template_name = 'daoistic/search_chapters.html'

    def get_queryset(self):
        """ Return chapters for the grid. """
        if not self.request.user.is_authenticated:
            if self.kwargs['book'] != '道德經':
                raise Http404() # Unauth'd users search only 道德經.
            if len(self.kwargs['chars']) > MAX_SEARCH_CHARS:
                raise Http404() # Unauth'd users too many search chars.
        try:
            Book.objects.get(title=self.kwargs['book'])
        except Book.DoesNotExist:
            raise Http404() # The requested book doesn't exist.
        for char in self.kwargs['chars']:
            try:
                UnihanCharacter.objects.get(pk=ord(char))
            except UnihanCharacter.DoesNotExist:
                raise Http404() # A search character doesn't exist.
        return Chapter.objects.filter(
            book__title=self.kwargs['book'],
            *[Q(hanzi__contains=char) for char in self.kwargs['chars']],
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        """ Insert study page data into index template. """
        context = super().get_context_data(**kwargs)
        context['brand_href'] = '/poems'
        context['brand_title'] = 'Poems home'
        context['book'] = self.kwargs['book']
        context['chars'] = self.kwargs['chars']
        return context

@method_decorator(cache_public(60 * 15), name='dispatch')
class StudyDetailView(DetailView):
    """ English/pinyin/hanzi chapter view. """

    model = Chapter
    template_name = 'daoistic/study_details.html'

    @classmethod
    def _add_chapter_data(cls, chapter):
        """ Return a list of stanza data and a dict that maps unihan
        characters to db objects. Stanzas contain lines that the template
        represents in three different ways, hanzi, pinyin, and English.
        The template uses the db objects to transform unihan characters
        for the hanzi/pinyin representations to modal popup buttons and
        pinyin, respectively. """
        hz_stanzas = re.split(
            '\n{2,}', str(normalize_newlines(chapter.hanzi))
        )
        en_stanzas = re.split(
            '\n{2,}', str(normalize_newlines(chapter.english))
        )
        stanzas = []
        hz_chars = set()
        if (
                (en_stanzas and hz_stanzas)
                and len(en_stanzas) == len(hz_stanzas)):
            for stanza_num, _ in enumerate(hz_stanzas):
                hz_lines = hz_stanzas[stanza_num].split('\n')
                en_lines = en_stanzas[stanza_num].split('\n')
                if len(en_lines) == len(hz_lines):
                    line_data = []
                    for line_num, _ in enumerate(hz_lines):
                        hz_line = hz_lines[line_num].translate(HANZI_TMAP)
                        hz_chars.update([hz for hz in hz_line])
                        line_data.append([
                            hz_line,
                            hz_line,
                            en_lines[line_num],
                        ])
                stanzas.append(line_data)
        chapter.stanzas = stanzas
        chapter.char_map = get_char_map(''.join(hz_chars))
        chapter.copyright_year = chapter.last_update.year

    def get_context_data(self, **kwargs):
        """ Insert study chapter info into index template. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Chapter %d | %s' % (
            self.kwargs['chapter'], self.object.title,
        )
        page_number = ((self.kwargs['chapter'] - 1) / 9) + 1
        if page_number == 1:
            context['brand_href'] = '/studies'
            context['brand_title'] = 'Studies home'
            context['poems_href'] = '/poems/chapter/%d' % self.object.number
            context['poems_title'] = 'Poems chapter %d' % self.object.number
            context['studies_href'] = '/studies'
            context['studies_title'] = 'Studies home'
        else:
            context['brand_href'] = '/studies/page/%d' % page_number
            context['brand_title'] = 'Studies page %d' % page_number
            context['poems_href'] = '/poems/chapter/%d' % self.object.number
            context['poems_title'] = 'Poems chapter %d' % self.object.number
            context['studies_href'] = '/studies/page/%d' % page_number
            context['studies_title'] = 'Studies page %d' % page_number
        if self.request.user.is_authenticated:
            context['compare'] = True
            context['compare_href'] = (
                '/compare/chapter/%d' % self.object.number
            )
            context['compare_title'] = (
                'Compare chapter %d versions' % self.object.number
            )
        return context

    def get_object(self, queryset=None):
        """ Return the chapter object to detail. """

        # Fetch/validate requested chapter.
        if 'chapter' not in self.kwargs:
            self.kwargs['chapter'] = 1
        try:
            filter_args = [Q(book__title='道德經')]
            if not self.request.user.is_authenticated:
                filter_args.append(Q(published=True))
            chapter = Chapter.objects.get(
                number=self.kwargs['chapter'],
                *filter_args,
            )
        except Chapter.DoesNotExist:
            raise Http404()

        # Add view-specific data to the object and return it.
        StudyDetailView._add_chapter_data(chapter)
        return chapter

@method_decorator(cache_public(60 * 15), name='dispatch')
class StudyListView(ListView):
    """ Study index grid view. """

    model = Chapter
    template_name = 'daoistic/study_list.html'

    @classmethod
    def _add_chapter_data(cls, chapter):
        """ Add a summary field to the chapter. """

        # English summary.
        english = chapter.english.split('\n', 1)[0].strip()
        if english.endswith(','):
            english = english[:-1]
        if not english.endswith('.'):
            english += '.'
        chapter.english_summary = english

        # Hanzi/pinyin summary.
        hanzi = chapter.hanzi.split('\n', 1)[0].strip()
        chapter.hanzi_summary = hanzi.translate(HANZI_TMAP)

    def get_context_data(self, *, object_list=None, **kwargs):
        """ Insert study page data into index template. """
        context = super().get_context_data(**kwargs)
        context['page_number'] = self.kwargs['page']
        context['page_title'] = 'Chapters %d-%d' % self.kwargs['chapters']
        context['brand_href'] = '/studies'
        context['brand_title'] = 'Studies home'
        context['studies_href'] = '/studies'
        context['studies_title'] = 'Studies home'
        if self.kwargs['page'] == 1:
            context['poems_href'] = '/poems'
            context['poems_title'] = 'Poems home'
        else:
            context['poems_href'] = '/poems/page/%d' % self.kwargs['page']
            context['poems_title'] = 'Poems page %d' % self.kwargs['page']
        hz_data = set()
        for chapter in context['object_list']:
            hz_data.update([hz for hz in chapter.hanzi_summary])
        context['char_map'] = get_char_map(''.join(hz_data))
        return context

    def get_queryset(self):
        """ Return chapters for the grid. """
        if 'page' not in self.kwargs:
            self.kwargs['page'] = 1
        self.kwargs['chapters'] = _chapter_range(self.kwargs['page'])
        chapters = Chapter.objects.filter(
            book__title='道德經',
            number__range=self.kwargs['chapters'],
            published=True,
        )
        for chapter in chapters:
            StudyListView._add_chapter_data(chapter)
        return chapters
