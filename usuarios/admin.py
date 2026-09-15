from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono'),
        }),
    )