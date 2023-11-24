""" Blog template tags module """
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
@stringfilter
def linkify(value, unihan_map):
    """ Convert unihan characters to links. """
    link = '<a class="unihan %s" href="#%s" title="%s - %s">%s</a>'
    converted = []
    if unihan_map:
        for char in value:
            if char in unihan_map:
                converted.append(link % (
                    unihan_map[char].utf8,
                    unihan_map[char].utf8,
                    unihan_map[char].pinyin,
                    unihan_map[char].definition,
                    unihan_map[char].utf8
                ))
            else:
                converted.append(char)
        return mark_safe(''.join(converted))
    return mark_safe(value)
