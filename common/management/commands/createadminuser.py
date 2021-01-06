""" Management utility to create the admin superuser. """
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS


class Command(BaseCommand):
    """ A command to create the admin superuser. """

    help = 'Used to create the admin superuser.'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        """ Add create admin superuser args. """
        parser.add_argument(
            'password',
            help='Specifies the admin user\'s password.',
        )

    def handle(self, *args, **options):
        """ Create the admin superuser. """
        user_model = get_user_model()

        # Validate user data.
        try:
            user_model._default_manager.db_manager(
                DEFAULT_DB_ALIAS
            ).get_by_natural_key('admin')
            raise CommandError('Admin user already exists.')
        except user_model.DoesNotExist:
            pass
        user_data = {
            user_model.USERNAME_FIELD: 'admin',
            'email': '',
            'password': options['password'],
        }
        try:
            validate_password(
                options['password'],
                user_model(**user_data)
            )
        except exceptions.ValidationError as err:
            raise CommandError(str(err))

        # Create superuser.
        user_model._default_manager.db_manager(
            DEFAULT_DB_ALIAS
        ).create_superuser(**user_data)
