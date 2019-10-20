""" Custom user admin module. """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from user.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """ Custom user admin tweaks. """

    add_form = UserCreationForm
    change_form = UserChangeForm
    readonly_fields = (
        'date_joined',
        'is_superuser',
        'last_login',
    )

    def get_queryset(self, request):
        """ Exclude superusers from query set for non-superusers. """
        qset = super(CustomUserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qset
        return qset.exclude(is_superuser__exact=True)

    def get_readonly_fields(self, request, obj=None):
        """ Allow only superusers to change superuser/user perms. """
        rof = super(CustomUserAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            rof += (
                'is_staff',
                'is_superuser',
                'user_permissions'
            )
        return rof

    def has_change_permission(self, request, obj=None):
        """ Allow only superusers to change superusers. """
        has = super(CustomUserAdmin, self).has_change_permission(request, obj)
        if obj and obj.is_superuser:
            if obj != request.user:
                has = False
        return has
