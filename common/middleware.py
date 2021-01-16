""" Common middleware module. """
from django.conf import settings
from django.http import Http404
from common import firewall


class FirewallMiddleware:
    """ Update admin address. Place after AuthenticationMiddleware. """
    # pylint: disable=too-few-public-methods

    def __init__(self, get_response):
        """ One time config and init. """
        self.get_response = get_response

    def __call__(self, request):
        """ Update admin group members' firewall address. """
        response = self.get_response(request)
        if (
                request.user.is_staff
                and request.path == '/admin/'
                and response.status_code == 200):
            admin_addr = request.session.get('admin_addr', None)
            request_addr = request.META['HTTP_X_REAL_IP']
            if (
                    not admin_addr
                    or (admin_addr and admin_addr != request_addr)):
                request.session['admin_addr'] = request_addr
                firewall.add_admin(request.session['admin_addr'])
        return response


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
