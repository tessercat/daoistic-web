""" Daoistic app admin module. """
from django.contrib import admin
from book.models import Book, Chapter


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """ Book admin tweaks. """

    fields = (
        'title',
        'subtitle',
    )
    list_display = (
        'title',
        'subtitle',
    )
    ordering = ('id',)

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_change_permission(self, request, obj=None):
        """ Disable change. """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """ Chapter admin tweaks. """

    @classmethod
    def _get_list_title(cls, obj):
        return '%s %d' % (obj.book, obj.number)

    _get_list_title.short_description = 'Chapter'

    fields = (
        'book',
        'number',
        'title',
        'last_english_update',
        'last_hanzi_update',
        'published',
        'english',
        'hanzi',
        'notes',
    )
    list_display = (
        '_get_list_title',
        'title',
        'last_english_update',
        'last_hanzi_update',
        'published',
    )
    ordering = ('id',)
    search_fields = (
        'english',
        'hanzi',
    )

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_change_permission(self, request, obj=None):
        """ Disable change. """
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False
