""" Common app config module. """
import logging
from fnmatch import fnmatch
import os
from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


common_settings = {}


class CommonConfig(AppConfig):
    """ Common app config. """
    name = 'common'

    def ready(self):
        """ Populated paths registry and configure CSS file. """
        # pylint: disable=import-outside-toplevel
        from django.conf import settings

        # Autodiscover protected paths configuration.
        autodiscover_modules('protected_paths')

        # Configure app settings.
        static_dir = os.path.join(
            settings.BASE_DIR, self.name, 'static', self.name
        )

        # Configure css setting.
        pattern = 'daoistic.?????.css'
        css_dir = os.path.join(static_dir, 'css')
        for filename in os.listdir(css_dir):
            if fnmatch(filename, pattern):
                common_settings['css'] = filename
                break

        # Configure js setting.
        pattern = 'daoistic.?????.js'
        js_dir = os.path.join(static_dir, 'js')
        for filename in os.listdir(js_dir):
            if fnmatch(filename, pattern):
                common_settings['js'] = filename
                break

        logger = logging.getLogger('django.server')
        for key, value in common_settings.items():
            logger.info('%s %s %s', self.name, key, value)
