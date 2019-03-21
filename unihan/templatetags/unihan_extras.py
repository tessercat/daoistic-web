""" Unihan template tags module """
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe


register = template.Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def pinyinify(value, char_map, autoescape=True):
    """ Convert unihan characters to pinyin and drop non-unihan
    characters not found in the char_map. . """
    autoescape = autoescape and not isinstance(value, SafeData)
    if autoescape:
        value = escape(value)
    converted = []
    for char in value:
        if char in char_map:
            converted.append(char_map[char].mandarin.split()[0])
    return mark_safe(' '.join(converted))

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def buttonify(value, char_map=None, autoescape=True):
    """ Convert unihan characters to modal popup buttons based on objects
    in the char_map, leaving non-unihan characters as-is. """
    autoescape = autoescape and not isinstance(value, SafeData)
    if autoescape:
        value = escape(value)
    button = (
        '<a class="btn btn-hanzi text-body" title="%s" role="button" '
        'onclick="unihanModal(event);" data-target="#unihanModal" '
        'data-char="%s">%s</a>'
    )
    converted = []
    for char in value:
        if char_map and char in char_map:
            obj = char_map[char]
            title = [obj.mandarin, obj.definition]
            title = [part for part in title if part]
            title = ' - '.join(title)
            converted.append(button % (title, char, char))
        else:
            converted.append(char)
    return mark_safe(''.join(converted))
