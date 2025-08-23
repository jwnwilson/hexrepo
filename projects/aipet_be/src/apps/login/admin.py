from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailVerification, PasswordReset, User

admin.site.register(EmailVerification)
admin.site.register(PasswordReset)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_verified", "is_staff", "is_active", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (("Verification", {"fields": ("is_verified",)}),)

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Verification", {"fields": ("is_verified",)}),
    )
