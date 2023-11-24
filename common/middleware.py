""" Common middleware module. """
from common import firewall


class AdminKnockMiddleware:
    """ Add request IP to admin set on login. Place after
    AuthenticationMiddleware. """
    # pylint: disable=too-few-public-methods

    def __init__(self, get_response):
        """ One time config and init. """
        self.get_response = get_response

    def __call__(self, request):
        """ Update admin group members' firewall address. """
        response = self.get_response(request)
        if response.status_code == 200 and request.user.is_staff:
            if (
                    'admin' in request.resolver_match.app_names
                    and request.resolver_match.url_name == 'index'):
                admin_addr = request.session.get('admin_addr', None)
                request_addr = request.META['HTTP_X_REAL_IP']
                if (
                        not admin_addr
                        or (admin_addr and admin_addr != request_addr)):
                    request.session['admin_addr'] = request_addr
                    firewall.add_admin(request.session['admin_addr'])
        return response
