""" Unihan app views module. """
import string
from django import forms
from django.views.generic.edit import FormView
from common.views import css_file
from unihan.models import UnihanCharacter


def is_candidate(char):
    """ A cheap test that a character might be unihan. """
    return char not in string.printable


def unihan_map(text, max_lookups=100):
    """ Return a map of unihan characters to db objects, possibly
    limiting the number of db lookups. """
    objects = {}
    lookups = 0
    # lookup_failures = []
    for char in text:
        if max_lookups and lookups >= max_lookups:
            break
        if char in objects:
            continue
        if is_candidate(char):
            try:
                objects[char] = UnihanCharacter.objects.get(pk=ord(char))
                lookups += 1
            except UnihanCharacter.DoesNotExist:
                # lookup_failures.append(char)
                pass
    # import logging
    # logging.getLogger('django.server').info(lookups)
    # logging.getLogger('django.server').info(lookup_failures)
    return objects


class UnihanForm(forms.Form):
    """ Unihan lookup form. """
    field = forms.CharField(widget=forms.Textarea, max_length=2500)


class UnihanFormView(FormView):
    """ Unihan lookup view. """
    form_class = UnihanForm
    template_name = 'unihan/form.html'

    def form_valid(self, form):
        """ Return the same form. Copied from form_invalid. """
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """ Insert template context data. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Unihan lookup'
        context['css_file'] = css_file()
        if context['form'].is_valid():
            context['form_data'] = context['form'].cleaned_data['field']
            if self.request.user.is_authenticated:
                context['char_map'] = unihan_map(context['form_data'], False)
            else:
                context['char_map'] = unihan_map(context['form_data'])
        else:
            context['form_data'] = ''
            context['char_map'] = {}
        return context
