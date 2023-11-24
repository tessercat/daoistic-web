""" Daoistic app admin module. """
from django.contrib import admin
from entry.models import Archive, Entry


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    """ Archive admin tweaks. """

    fields = (
        'title',
        'subtitle',
        'slug',
    )
    list_display = (
        'title',
        'subtitle',
        'slug',
    )
    ordering = ('slug',)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """ Entry admin tweaks. """

    fields = (
        'title',
        'archive',
        'lede',
        'weight',
        'copyright_year',
        'last_update',
        'slug',
        'published',
        'entry_type',
    )
    list_display = (
        'title',
        'archive',
        'weight',
        'copyright_year',
        'last_update',
        'slug',
        'published',
    )
    ordering = ('-last_update',)
