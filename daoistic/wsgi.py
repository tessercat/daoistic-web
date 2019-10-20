""" Project WSGI config. """
import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daoistic.settings')
application = get_wsgi_application()
