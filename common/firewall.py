""" Firewall API module. """
from django.conf import settings
import httpx


def add_admin(address):
    """ Add an address to the admin set. """
    params = {'address': address, 'ipset': 'admin'}
    response = httpx.put(
        f'http://localhost:{settings.FIREWALL_API_PORT}',
        params=params
    )
    response.raise_for_status()
