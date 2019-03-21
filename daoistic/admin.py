""" Daoistic app admin module. """
from django.contrib import admin
from django.utils import timezone
from daoistic.models import Book, Chapter


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
        'last_update',
        'published',
        'english',
        'hanzi',
        'notes',
    )
    list_display = (
        '_get_list_title',
        'title',
        'last_update',
        'published',
    )
    ordering = ('id',)
    search_fields = (
        'english',
        'hanzi',
    )

    def get_readonly_fields(self, request, obj=None):
        """ Only expires is editable after creation. """
        fields = super(ChapterAdmin, self).get_readonly_fields(request, obj)
        if obj and obj.book and obj.book.title == '道德經':
            fields += (
                'book',
                'last_update',
                'number',
            )
        return fields

    def has_add_permission(self, request):
        """ Disable add. """
        return False

    def has_change_permission(self, request, obj=None):
        """ Disable change except for 道德經. """
        if obj and obj.book and obj.book.title == '道德經':
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """ Disable delete. """
        return False

    def save_model(self, request, obj, form, change):
        """ Update last update timestamp on save. """
        update_fields = ('title', 'english', 'hanzi')
        if any(field in update_fields for field in form.changed_data):
            obj.last_update = timezone.now()
            form.changed_data.append('last_update')
        super().save_model(request, obj, form, change)
