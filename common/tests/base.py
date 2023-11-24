""" Test case base module. """
import logging
from django.test import TestCase


class BaseTestCase(TestCase):
    """ Parent class with nice things. """

    def setUp(self):
        """ Log everything to the console. """
        logging.disable(logging.NOTSET)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

    @staticmethod
    def _log(data):
        """ Log data to the django.server info logger. """
        logging.getLogger('django.server').info(data)
