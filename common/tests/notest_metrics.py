""" Metrics endpoint test module. """
from django.conf import settings
from common.tests.base import BaseTestCase


class MetricsTestCase(BaseTestCase):
    """ Verify metrics responses. """

    def test_metrics_fqdnhost(self):
        """ Assert GET metrics endpoint from not-localhost returns 404. """
        response = self.client.get(
            '/metrics',
            HTTP_X_FORWARDED_HOST=settings.ALLOWED_HOSTS[0],
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason_phrase, 'Not Found')
        self.assertEqual(response.templates[0].name, 'common/error.html')

    def test_metrics_localhost(self):
        """ Assert GET metrics endpoint from localhost returns 200. """
        response = self.client.get(
            '/metrics',
            HTTP_X_FORWARDED_HOST='localhost',
        )
        self.assertEqual(response.status_code, 200)
