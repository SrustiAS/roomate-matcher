from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "full_name", "email", "hostel", "preferred_floor",
                    "year", "is_blocked", "is_active")
    list_filter = ("hostel", "preferred_floor", "year", "is_blocked", "is_active")
    search_fields = ("username", "full_name", "email", "branch", "hostel")
    actions = ["block_users", "unblock_users"]

    # Password hashes are shown read-only by UserAdmin and never in plain text.
    fieldsets = UserAdmin.fieldsets + (
        ("Student profile", {
            "fields": ("full_name", "age", "gender", "college", "branch", "year",
                       "cgpa", "hostel", "preferred_floor", "current_floor",
                       "phone", "contact_preference", "is_blocked"),
        }),
    )

    @admin.action(description="Block selected users")
    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description="Unblock selected users")
    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
