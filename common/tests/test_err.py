""" Error test module. """
from django.conf import settings
from common.tests.base import BaseTestCase


class ErrTestCase(BaseTestCase):
    """ Verify error responses. """

    def test_fqdnhost_404(self):
        """ Assert GET non-existent URL returns 404. """
        response = self.client.get(
            '/nosuchurl',
            HTTP_X_FORWARDED_HOST=settings.ALLOWED_HOSTS[0],
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason_phrase, 'Not Found')
        self.assertEqual(response.templates[0].name, 'common/error.html')

    # TODO 400 and 403.
