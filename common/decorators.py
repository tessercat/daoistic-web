""" Custom decorators module. """
from functools import wraps
from django.views.decorators.cache import cache_page


def cache_public(timeout):
    """ Decorator to return cached pages for normal requests,
    but bypass cache for staff. """

    def decorator(function):
        """ Inner decorator. """

        @wraps(function)
        def wrap(request, *args, **kwargs):
            """ Return the function, possibly wrapped in cache_page. """
            if request.user.is_staff:
                return function(request, *args, **kwargs)
            return cache_page(timeout)(function)(request, *args, **kwargs)
        return wrap

    return decorator
