""" Daoistic app admin module. """
from django.contrib import admin
from blog.models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """ Entry admin tweaks. """

    fields = (
        'title',
        'lede',
        'last_update',
        'slug',
        'published',
    )
    list_display = (
        'title',
        'last_update',
        'slug',
        'published',
    )
    ordering = ('-last_update',)
