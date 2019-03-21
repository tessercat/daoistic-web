""" Unihan app views module. """
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from unihan.forms import DictionaryForm, DumpForm
from unihan.models import UnihanCharacter
from unihan.tools import get_char_map


MAX_LOOKUPS = 50

class DictionaryView(FormView):
    """ Unihan dictionary view. """

    form_class = DictionaryForm
    template_name = 'unihan/dictionary.html'

    def form_valid(self, form):
        """ Return the same form. Copied from form_invalid. """
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """ Insert dictionary context data. """
        context = super().get_context_data(**kwargs)
        context['brand_href'] = '/'
        context['brand_title'] = 'Home'
        if context.get('form') and context['form'].is_valid():
            context['char'] = context['form'].cleaned_data['search']
            context['char_map'] = {}
        return context

    def get_success_url(self):
        """ Return to the same page. """
        return ''

class DumpView(FormView):
    """ Unihan dump view. """

    form_class = DumpForm
    template_name = 'unihan/dump.html'

    def form_valid(self, form):
        """ Return the same form. Copied from form_invalid. """
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """ Insert dump context data. """
        context = super().get_context_data(**kwargs)
        context['brand_href'] = '/'
        context['brand_title'] = 'Home'
        if context.get('form') and context['form'].is_valid():
            context['dump_data'] = context['form'].cleaned_data['hanzi']
            if self.request.user.is_authenticated:
                max_lookups = False
            else:
                max_lookups = MAX_LOOKUPS
            context['char_map'] = get_char_map(
                context['dump_data'], max_lookups,
            )
        else:
            context['dump_data'] = ''
            context['char_map'] = {}
        return context

@method_decorator(cache_page(60 * 15), name='dispatch')
class CharDetailView(DetailView):
    """ Unihan character detail view. """

    model = UnihanCharacter
    template_name = 'unihan/char_info.html'

    def get_object(self, queryset=None):
        """ Return a character object. """
        if 'char' not in self.kwargs or len(self.kwargs['char']) != 1:
            raise Http404()
        try:
            obj = UnihanCharacter.objects.get(
                pk=ord(self.kwargs['char'])
            )
        except UnihanCharacter.DoesNotExist:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        """ Insert character detail context data. """
        context = super().get_context_data(**kwargs)
        char = context['object']
        context['char'] = char
        hz_data = set([char.utf8, char.radical.utf8])
        hz_data.update([hz for hz in char.semantic_variants])
        hz_data.update([hz for hz in char.simplified_variants])
        hz_data.update([hz for hz in char.traditional_variants])
        context['char_map'] = get_char_map(''.join(hz_data))
        return context
