""" Unihan app views module. """
import logging
import string
from django import forms
from django.views.generic.edit import FormView
from unihan.models import UnihanCharacter


def get_block(char):
    """ Return the character's tr38 block number or -1. """
    block = -1

    try:
        codepoint = ord(char)
    except TypeError:
        return block

    # A slightly cheaper test up front.
    if char in string.printable:
        return block

    # https://www.unicode.org/reports/tr38/#BlockListing
    # https://www.unicode.org/reports/tr38/#SortingAlgorithm

    match codepoint:
        # CJK Unified Ideographs
        case codepoint if 0x4E00 <= codepoint <= 0x9FFF:
            block = 0
        # CJK Unified Ideographs Extension A
        case codepoint if 0x3400 <= codepoint <= 0x4DBF:
            block = 1
        # CJK Unified Ideographs Extension B
        case codepoint if 0x20000 <= codepoint <= 0x2A6DF:
            block = 2
        # CJK Unified Ideographs Extension C
        case codepoint if 0x2A700 <= codepoint <= 0x2B739:
            block = 3
        # CJK Unified Ideographs Extension D
        case codepoint if 0x2B740 <= codepoint <= 0x2B81D:
            block = 4
        # CJK Unified Ideographs Extension E
        case codepoint if 0x2B820 <= codepoint <= 0x2CEA1:
            block = 5
        # CJK Unified Ideographs Extension F
        case codepoint if 0x2CEB0 <= codepoint <= 0x2EBE0:
            block = 6
        # CJK Unified Ideographs Extension G
        case codepoint if 0x30000 <= codepoint <= 0x3134A:
            block = 7
        # CJK Unified Ideographs Extension H
        case codepoint if 0x31350 <= codepoint <= 0x323AF:
            block = 8
        # CJK Unified Ideographs Extension I
        case codepoint if 0x2EBF0 <= codepoint <= 0x2EE5D:
            block = 9
        # CJK Compatibility Ideographs
        case codepoint if 0xF900 <= codepoint <= 0xFAD9:
            block = 254
        # CJK Compatibility Supplement
        case codepoint if 0x2F800 <= codepoint <= 0x2FA1D:
            block = 255
    return block


def is_unihan(char):
    """ Return True if the character's codepoint is in a Unihan block. """
    return get_block(char) >= 0


def unihan_map(text, max_lookups=250, ctext_target='dictionary'):
    """ Return a map of unihan characters to db objects. """
    objects = {}
    lookups = 0
    lookup_failures = []
    for char in text:
        if max_lookups and lookups >= max_lookups:
            break
        if char in objects:
            continue
        if is_unihan(char) and char not in lookup_failures:
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
    field = forms.CharField(
        widget=forms.Textarea(attrs={'autofocus': True}),
        max_length=5000
    )


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
        context['page_title'] = 'Unihan Lookup'
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
