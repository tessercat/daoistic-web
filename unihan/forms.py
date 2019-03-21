""" Unihan forms module. """
from django import forms
from django.core.exceptions import ValidationError
from unihan.models import UnihanCharacter


class SearchField(forms.CharField):
    """ Unihan dictionary search filed. """

    def to_python(self, value):
        """ Return a UnihanCharacter object. """
        if len(value) != 1:
            raise ValidationError(
                (
                    'Use the dictionary to look up single characters. '
                    'The Unihan dump page is for studying longer passages.'
                ),
                code='invalid',
            )
        try:
            obj = UnihanCharacter.objects.get(pk=ord(value))
        except UnihanCharacter.DoesNotExist:
            raise ValidationError(
                'Not found in Unihan data',
                code='invalid'
            )
        return obj

class DictionaryForm(forms.Form):
    """ Unihan dictionary search form. """

    search = SearchField()

class DumpForm(forms.Form):
    """ Unihan dump form. """

    hanzi = forms.CharField(widget=forms.Textarea)
