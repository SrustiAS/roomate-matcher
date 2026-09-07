from django.contrib import admin
from .models import Preference, RoommateRequest, Room


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "sleep_type", "light_preference", "noise_preference",
                    "cleanliness", "updated_at")
    list_filter = ("sleep_type", "light_preference", "noise_preference", "cleanliness")
    search_fields = ("user__username", "user__full_name")


@admin.register(RoommateRequest)
class RoommateRequestAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("sender__username", "receiver__username")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("hostel", "floor", "room_number", "capacity", "available_beds")
    list_filter = ("hostel", "floor")
    search_fields = ("room_number", "hostel")
