""" Daoistic app admin module. """
from django.contrib import admin
from blog.models import Archive, Entry


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
        'first_published',
        'last_update',
        'slug',
        'published',
        'allow_hanzi',
    )
    list_display = (
        'title',
        'archive',
        'first_published',
        'last_update',
        'slug',
        'published',
    )
    ordering = ('-first_published',)
