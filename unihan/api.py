""" A Module interface to the unihan app. """
from unihan.models import UnihanCharacter


def unihan_map(text, max_lookups=False):
    """ Return a map of unihan characters to db objects, possibly
    limiting the number of db lookups. """
    lookups = 0
    objects = {}
    for char in text:
        if (
                (max_lookups and lookups <= max_lookups)
                or not max_lookups):
            try:
                lookups += 1
                objects[char] = UnihanCharacter.objects.get(pk=ord(char))
            except UnihanCharacter.DoesNotExist:
                pass
    return objects
