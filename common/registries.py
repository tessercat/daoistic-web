""" Common registries module. """
import logging


class _PathsRegistry:
    """ Protected paths registry. """
    # pylint: disable=too-few-public-methods

    _registry = []
    registry = _registry


# settings.COMMON_PROTECTED_PATHS
common_protected_paths_registry = _PathsRegistry()


def register_protected_path(path):
    """ Add paths to the global protected paths registry."""
    common_protected_paths_registry.registry.append(path)
    logging.getLogger('django.server').info(
        'Registered protected path %s', path
    )
