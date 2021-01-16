""" Firewall API module. """
from django.conf import settings
import httpx


def accept(transport, start, end):
    """ Allow IPv4 and IPv6 traffic to the transport/port-range. """
    response = httpx.post(
        'http://localhost:%s/iptables/input/accept' % (
            settings.FIREWALL_API_PORT,
        ),
        data={
            'action': 'add',
            'transport': transport,
            'start': start,
            'end': end,
        }
    )
    response.raise_for_status()


def add_admin(address):
    """ Add an address to the admin set. """

    # Set the entry address.
    response = httpx.post(
        'http://localhost:%s/ipset/admin' % settings.FIREWALL_API_PORT,
        data={'address': address}
    )
    response.raise_for_status()
