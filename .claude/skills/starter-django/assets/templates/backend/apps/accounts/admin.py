from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "clerk_id", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "clerk_id")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Clerk", {"fields": ("clerk_id",)}),
    )
