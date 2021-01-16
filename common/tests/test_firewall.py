""" Common app session test module. """
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from firewall.tests.base import CommonTestCase


class FirewallTestCase(CommonTestCase):
    """ Verify that firewall/signals/middleware act as expected. """

    @staticmethod
    def _login(client):
        """ Log a client in as superuser. """
        client.get('/admin/login/')
        get_user_model().objects.create_superuser(
            'username', password='password', email='admin@example.com',
        )
        client.post(
            '/admin/login/',
            data={'username': 'username', 'password': 'password'},
            follow=True,
        )

    @staticmethod
    def _logout(client):
        """ Log the client out. """
        client.get('/admin/logout/')

    def test_login_signal(self):
        """ Assert that the expected address is in the session. """
        expected_addr = '10.4.4.40'
        client = Client(
            HTTP_X_FORWARDED_HOST=settings.ALLOWED_HOSTS[0],
            HTTP_X_REAL_IP=expected_addr,
        )
        FirewallTestCase._login(client)
        addr = client.session['admin_addr']
        FirewallTestCase._logout(client)

        # Assert after logout.
        self.assertEqual(addr, expected_addr)

    def test_middleware(self):
        """ Assert that the admin address changes. """
        initial_addr = '10.4.4.50'
        expected_addr = '10.4.4.60'
        client = Client(
            HTTP_X_FORWARDED_HOST=settings.ALLOWED_HOSTS[0],
            HTTP_X_REAL_IP=initial_addr,
        )
        FirewallTestCase._login(client)
        actual_initial_addr = client.session['admin_addr']
        client.defaults['HTTP_X_REAL_IP'] = expected_addr
        client.get('/admin/')
        actual_expected_addr = client.session['admin_addr']
        FirewallTestCase._logout(client)

        # Assert after logout.
        self.assertEqual(actual_initial_addr, initial_addr)
        self.assertEqual(actual_expected_addr, expected_addr)
