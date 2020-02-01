""" Blog app models module. """
from datetime import date
from django.db import models


class Entry(models.Model):
    """ A blog entry. """

    class Meta:
        """ Model meta tweaks. """
        verbose_name_plural = 'Entries'

    allow_hanzi = models.BooleanField(
        default=False,
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

    def get_absolute_url(self):
        """ Return the blog url. """
        return '/blog/%s' % self.slug

    def __str__(self):
        return self.title
