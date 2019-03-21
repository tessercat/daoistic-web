""" Daoistic decorators module. """
from functools import wraps
from django.views.decorators.cache import cache_page


def cache_public(timeout):
    """ Decorator to cache pages for unauthorized users, but bypass cache
    for logged-in users, https://stackoverflow.com/questions/11661503. """

    def decorator(function):
        """ Inner decorator. """

        @wraps(function)
        def wrap(request, *args, **kwargs):
            """ Return the function, possibly wrapped in cache_page. """
            if request.user.is_authenticated:
                return function(request, *args, **kwargs)
            return cache_page(timeout)(function)(request, *args, **kwargs)
        return wrap

    return decorator
