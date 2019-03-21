""" Unihan app models module. """
from django.db import models


class UnihanCharacter(models.Model):
    """ A Unihan character. Has-a UnihanRadical. """

    codepoint = models.IntegerField(
        primary_key=True,
    )
    definition = models.TextField(
        max_length=1000,
    )
    mandarin = models.CharField(
        max_length=20,
    )
    radical = models.ForeignKey(
        'UnihanRadical',
        on_delete=models.SET_NULL,
        null=True,
    )
    residual_strokes = models.IntegerField(
    )
    simplified_variants = models.CharField(
        max_length=10,
    )
    traditional_variants = models.CharField(
        max_length=10,
    )
    semantic_variants = models.CharField(
        max_length=10,
    )
    sort_order = models.IntegerField(
    )
    utf8 = models.CharField(
        max_length=1,
    )

    class Meta:
        """ Model meta tweaks. """
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'

    def __str__(self):
        return self.utf8

class UnihanRadical(models.Model):
    """ A Unihan radical. Is-a UnihanCharacter. """

    character = models.OneToOneField(
        'UnihanCharacter',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    radical_number = models.IntegerField()
    simplified = models.BooleanField()
    utf8 = models.CharField(
        max_length=1,
    )

    class Meta:
        """ Model meta tweaks. """
        verbose_name = 'Radical'
        verbose_name_plural = 'Radicals'

    def __str__(self):
        return self.utf8
