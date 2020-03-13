""" Daoistic app admin module. """
from django.contrib import admin
from blog.models import Entry


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    """ Entry admin tweaks. """

    fields = (
        'title',
        'lede',
        'first_published',
        'last_update',
        'slug',
        'published',
        'allow_hanzi',
    )
    list_display = (
        'title',
        'first_published',
        'last_update',
        'slug',
        'published',
    )
    ordering = ('-first_published',)
