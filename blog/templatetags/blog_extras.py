""" Blog template tags module """
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter(is_safe=True, needs_autoescape=False)
@stringfilter
def buttonify(value, char_map=None):
    """ Convert unihan characters to buttons based on objects in the
    char_map, leaving non-unihan characters as-is. """
    button = (
        '<a class="ctext-link" title="%s" '
        'target="_blank" rel="noopener noreferrer nofollow" '
        'href="https://ctext.org/dictionary.pl?if=en&char=%s">%s</a>'
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
    return ''.join(converted)
