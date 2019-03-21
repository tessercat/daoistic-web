""" Unihan admin module. """
from django.contrib import admin
from unihan.models import UnihanCharacter, UnihanRadical


@admin.register(UnihanCharacter)
class CharacterAdmin(admin.ModelAdmin):
    """ UnihanCharacter admin tweaks. """

    ordering = ('sort_order',)
    list_display = (
        'utf8',
        'mandarin',
        'radical',
        'residual_strokes',
        'traditional_variants',
        'simplified_variants',
        'semantic_variants',
        'sort_order',
        'definition',
    )
    search_fields = (
        'definition',
        'mandarin',
        'radical__utf8',
        'traditional_variants',
        'simplified_variants',
        'semantic_variants',
        'utf8',
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

@admin.register(UnihanRadical)
class RadicalAdmin(admin.ModelAdmin):
    """ UnihanRadical admin tweaks. """

    ordering = ('radical_number',)
    list_display = (
        'character',
        'mandarin',
        'radical_number',
        'simplified',
    )
    search_fields = (
        'utf8',
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

    def mandarin(self, obj):
        return obj.character.mandarin
