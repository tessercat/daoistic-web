""" Custom user module module. """
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ Override default user as recommended in Django docs. """
