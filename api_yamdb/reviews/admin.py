from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Register the User model in the admin panel"""
    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'password',
    )
