""" Daoistic app template tags module """
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe


register = template.Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def highlight(value, chars, autoescape=True):
    """ Wrap all chars in spans with class "highlight". """
    autoescape = autoescape and not isinstance(value, SafeData)
    if autoescape:
        value = escape(value)
    for char in chars:
        value = value.replace(
            char, '<span class="highlight">%s</span>' % char
        )
    return mark_safe(value)
