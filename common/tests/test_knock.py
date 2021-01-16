""" Port knock test module. """
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from common.tests.base import BaseTestCase


class PortKnockTestCase(BaseTestCase):
    """ Verify port knocking. """

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

    def test_admin_knock(self):
        """ Assert that session admin address changes. """
        expected_addr = '10.4.4.60'
        client = Client(
            HTTP_X_FORWARDED_HOST=settings.ALLOWED_HOSTS[0],
            HTTP_X_REAL_IP=expected_addr,
        )
        PortKnockTestCase._login(client)
        client.get('/admin/')
        actual_addr = client.session.get('admin_addr')
        PortKnockTestCase._logout(client)
        self.assertEqual(actual_addr, expected_addr)
