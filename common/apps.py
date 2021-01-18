""" Common app config module. """
from fnmatch import fnmatch
import os
from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from common.registries import common_protected_paths_registry


class CommonConfig(AppConfig):
    name = 'common'

    def ready(self):
        """ Populated paths registry and configure CSS file. """

        # Autodiscover protected paths configuration.
        autodiscover_modules(
            'protected_paths', register_to=common_protected_paths_registry
        )

        # Configure common CSS file.
        # pylint: disable=import-outside-toplevel
        import logging
        from django.conf import settings

        pattern = 'daoistic.?????.css'
        app_dir = os.path.join(
            settings.BASE_DIR, 'common', 'static', 'common', 'css'
        )
        logging.getLogger('django.server').info('Configuring COMMON_CSS')
        for filename in os.listdir(app_dir):
            if fnmatch(filename, pattern):
                settings.COMMON_CSS = filename
                logging.getLogger('django.server').info(
                    'Configured COMMON_CSS %s', filename
                )

        pattern = 'daoistic.?????.js'
        app_dir = os.path.join(
            settings.BASE_DIR, 'common', 'static', 'common', 'js'
        )
        logging.getLogger('django.server').info('Configuring COMMON_JS')
        for filename in os.listdir(app_dir):
            if fnmatch(filename, pattern):
                settings.COMMON_JS = filename
                logging.getLogger('django.server').info(
                    'Configured COMMON_JS %s', filename
                )
