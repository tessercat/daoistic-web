""" Blog app models module. """
from datetime import date
from django.db import models


class Archive(models.Model):
    """ An archive of blog entries. """
    slug = models.SlugField(
        max_length=15,
        unique=True,
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
    """ A blog entry. """

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
    first_published = models.DateField(
        default=date.today,
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
        max_length=15,
        unique=True,
    )
    title = models.CharField(
        max_length=100,
    )
    weight = models.PositiveSmallIntegerField(
        default=0,
    )

    def get_absolute_url(self):
        """ Return the blog url. """
        return '/blog/%s' % self.slug

    def __str__(self):
        return self.title
