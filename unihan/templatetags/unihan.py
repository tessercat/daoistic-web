""" Blog template tags module """
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def linkify(value, char_map):
    """ Convert unihan characters to links. """
    link = '<a class="unihan" href="#%s" title="%s - %s">%s</a>'
    converted = []
    if char_map:
        for char in value:
            if char in char_map:
                converted.append(link % (
                    char_map[char].utf8,
                    char_map[char].mandarin,
                    char_map[char].definition,
                    char_map[char].utf8
                ))
            else:
                converted.append(char)
        return mark_safe(''.join(converted))
    return mark_safe(value)
