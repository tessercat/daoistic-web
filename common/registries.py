""" Common registries module. """
import logging


protected_paths_registry = []


def register_protected_path(path):
    """ Add paths to the global protected paths registry."""
    protected_paths_registry.append(path)
    logging.getLogger('django.server').info(
        'Registered protected path %s', path
    )
