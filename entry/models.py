""" Entry app models module. """
from datetime import date
from django.db import models


class Archive(models.Model):
    """ An archive of entries. """
    slug = models.SlugField(
        max_length=15,
        unique=True,
    )
    image = models.SlugField(
        max_length=15,
        default='',
    )
    title = models.CharField(
        max_length=30,
    )
    subtitle = models.CharField(
        max_length=100,
    )
    # Archive.objects.entry_set.all()

    def __str__(self):
        return self.title


class Entry(models.Model):
    """ An entry. """

    class Meta:
        """ Model meta tweaks. """
        verbose_name_plural = 'Entries'

    entry_type = models.CharField(
        default='study',
        max_length=16,
    )
    archive = models.ForeignKey(
        'Archive',
        null=True,
        on_delete=models.SET_NULL
    )
    copyright_year = models.CharField(
        default='',
        max_length=4
    )
    last_update = models.DateField(
        default=date.today,
    )
    lede = models.CharField(
        max_length=250,
    )
    published = models.BooleanField(
        default=False,
    )
    slug = models.SlugField(
        max_length=25,
        unique=True,
    )
    title = models.CharField(
        max_length=100,
    )
    weight = models.PositiveSmallIntegerField(
        default=0,
    )

    def __str__(self):
        return self.title
