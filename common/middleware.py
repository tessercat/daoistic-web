""" Common middleware module. """
from django.conf import settings
from django.http import Http404


class ProtectedPathsMiddleware:
    """ Drop non-local requests for protected paths. """
    # pylint: disable=too-few-public-methods

    def __init__(self, get_response):
        """ One time config and init. """
        self.get_response = get_response

    def __call__(self, request):
        """ Return 404 for non-local requests to protected paths. """
        if request.get_host() != 'localhost':
            for path in settings.PROTECTED_PATHS:
                if request.path_info.startswith(path):
                    raise Http404
        return self.get_response(request)
