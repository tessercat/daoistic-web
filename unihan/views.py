""" Unihan app views module. """
import logging
import string
from django import forms
from django.views.generic.edit import FormView
from common.apps import common_settings
from unihan.models import UnihanCharacter


def get_block(char):
    """ Return the character's tr38 block number or -1. """
    # pylint: disable=too-many-return-statements
    try:
        codepoint = ord(char)
    except TypeError:
        return -1

    # https://www.unicode.org/reports/tr38/#BlockListing
    # https://www.unicode.org/reports/tr38/#SortingAlgorithm
    if 0x20000 <= codepoint <= 0x2A6DD:
        # CJK Unified Ideographs Extension B U+20000..U+2A6DD
        return 2
    if 0x4E00 <= codepoint <= 0x9FFC:
        # CJK Unified Ideographs U+4E00..U+9FFC
        return 0
    if 0x3400 <= codepoint <= 0x4DBF:
        # CJK Unified Ideographs Extension A U+3400..U+4DBF
        return 1
    if 0x2A700 <= codepoint <= 0x2B734:
        # CJK Unified Ideographs Extension C U+2A700..U+2B734
        return 3
    if 0x2B740 <= codepoint <= 0x2B81D:
        # CJK Unified Ideographs Extension D U+2B740..U+2B81D
        return 4
    if 0x2B820 <= codepoint <= 0x2CEA1:
        # CJK Unified Ideographs Extension E U+2B820..U+2CEA1
        return 5
    if 0x2CEB0 <= codepoint <= 0x2EBE0:
        # CJK Unified Ideographs Extension F U+2CEB0..U+2EBE0
        return 6
    if 0x30000 <= codepoint <= 0x3134A:
        # CJK Unified Ideographs Extension G U+30000..U+3134A
        return 7
    if 0xF900 <= codepoint <= 0xFAD9:
        # CJK Compatibility Ideographs U+F900..U+FAD9
        return 254
    if 0x2F800 <= codepoint <= 0x2FA1D:
        # CJK Compatibility Supplement U+2F800..U+2FA1D
        return 255
    return -1


def is_unihan(char):
    """ Return True if the character's codepoint is in a Unihan block. """
    if char in string.printable:
        return False  # A cheap test up front.
    return get_block(char) >= 0


def unihan_map(text, max_lookups=100, ctext_target='dictionary'):
    """ Return a map of unihan characters to db objects. """
    objects = {}
    lookups = 0
    lookup_failures = []
    for char in text:
        if max_lookups and lookups >= max_lookups:
            break
        if char in objects:
            continue
        if is_unihan(char):
            try:
                lookups += 1
                objects[char] = UnihanCharacter.objects.get(pk=ord(char))
                objects[char].ctext_target = ctext_target
            except UnihanCharacter.DoesNotExist:
                lookup_failures.append(char)
    # logging.getLogger('django.server').info(lookups)
    if lookup_failures:
        logging.getLogger('django.server').info(lookup_failures)
    return objects


class UnihanForm(forms.Form):
    """ Unihan lookup form. """
    field = forms.CharField(widget=forms.Textarea, max_length=2500)


class UnihanFormView(FormView):
    """ Unihan lookup view. """
    form_class = UnihanForm
    template_name = 'unihan/lookup.html'

    def form_valid(self, form):
        """ Return the same form. Copied from form_invalid. """
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """ Insert template context data. """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Unihan lookup'
        context['css'] = common_settings.get('css')
        context['js'] = common_settings.get('js')
        if context['form'].is_valid():
            context['form_data'] = context['form'].cleaned_data['field']
            if self.request.user.is_authenticated:
                context['unihan_map'] = unihan_map(
                    context['form_data'], False, 'search'
                )
            else:
                context['unihan_map'] = unihan_map(context['form_data'])
        else:
            context['form_data'] = ''
            context['unihan_map'] = {}
        return context
