""" Daoistic app models module. """
from datetime import date
from django.core.exceptions import ValidationError
from django.db import models


def validate_chapter_number(value):
    """ Raise ValidationError on invalid chapter number. """
    err = 'Chapter number must be an integer in the range 1-81.'
    try:
        int(value)
        assert 1 <= value <= 81
    except ValueError:
        raise ValidationError(err)
    except AssertionError:
        raise ValidationError(err)


class Book(models.Model):
    """ A verion of the Dao De Jing. """

    subtitle = models.CharField(
        max_length=25,
    )
    title = models.CharField(
        max_length=10,
    )

    def __str__(self):
        return '%s %s' % (self.title, self.subtitle)


class Chapter(models.Model):
    """ A chapter of a version of the Dao De Jing. """

    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
    )
    english = models.TextField(
        blank=True,
        default='',
    )
    hanzi = models.TextField(
        blank=True,
        default='',
    )
    last_english_update = models.DateField(
        default=date.today,
    )
    last_hanzi_update = models.DateField(
        default=date.today,
    )
    notes = models.TextField(
        blank=True,
        default='',
    )
    number = models.IntegerField(
        validators=[validate_chapter_number],
    )
    published = models.BooleanField()
    publish_notes = models.BooleanField()
    title = models.CharField(
        blank=True,
        default='',
        max_length=100,
    )

    def get_absolute_url(self):
        """ Return the chapter url. """
        return '/studies/%i' % self.number

    def __str__(self):
        if self.title:
            return '%s %s' % (self.number, self.title)
        return str(self.number)
