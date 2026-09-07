from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Preference(models.Model):
    """
    Lifestyle questionnaire answers (the 'Preferences' table from the spec).
    One-to-one with a user.
    """

    SLEEP_TYPE = [("night_owl", "🌙 Night Owl"), ("early_bird", "☀️ Early Bird / Day Bird")]

    LIGHT = [
        ("off", "Need lights OFF while sleeping"),
        ("dim", "Prefer dim / night light"),
        ("dont_mind", "Don't mind lights"),
        ("on_study", "Prefer lights ON while studying"),
    ]

    STUDY = [
        ("room", "Study mostly in the room"),
        ("library", "Study mostly in library"),
        ("occasional", "Study occasionally"),
        ("late_night", "Study late at night"),
        ("early_morning", "Study early morning"),
    ]

    NOISE = [
        ("quiet", "Need a very quiet room"),
        ("moderate", "Prefer moderate noise"),
        ("dont_mind", "Don't mind noise"),
    ]

    CLEAN = [
        ("very", "Very clean"),
        ("moderate", "Moderately clean"),
        ("relaxed", "Relaxed about cleanliness"),
    ]

    SOCIAL = [
        ("very", "Very social"),
        ("moderate", "Moderately social"),
        ("private", "Quiet / private"),
    ]

    VISITOR = [
        ("none", "Prefer no visitors"),
        ("occasional", "Occasional visitors are okay"),
        ("okay", "Visitors are okay"),
    ]

    ROOM_TYPE = [
        ("single", "Single"),
        ("double", "Double sharing"),
        ("triple", "Triple sharing"),
        ("any", "Any"),
    ]

    ROOM_LOCATION = [
        ("corner", "Corner room"),
        ("middle", "Middle of corridor"),
        ("near_stairs", "Near stairs / exit"),
        ("any", "Any"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences"
    )

    # Sleep
    sleep_type = models.CharField(max_length=12, choices=SLEEP_TYPE)
    sleep_time = models.TimeField(help_text="Typical time you fall asleep")
    wake_time = models.TimeField(help_text="Typical time you wake up")
    quiet_hours = models.CharField(max_length=60, blank=True, help_text="e.g. 11 PM – 7 AM")

    # Preferences
    light_preference = models.CharField(max_length=12, choices=LIGHT)
    study_habit = models.CharField(max_length=14, choices=STUDY)
    noise_preference = models.CharField(max_length=12, choices=NOISE)
    cleanliness = models.CharField(max_length=10, choices=CLEAN)
    social_level = models.CharField(max_length=10, choices=SOCIAL)
    visitor_preference = models.CharField(max_length=12, choices=VISITOR)

    # Hostel preferences
    preferred_room_type = models.CharField(max_length=10, choices=ROOM_TYPE, default="any")
    preferred_room_location = models.CharField(max_length=12, choices=ROOM_LOCATION, default="any")
    ok_with_other_branch = models.BooleanField(default=True)
    ok_with_other_year = models.BooleanField(default=True)

    # Optional habits
    eating_in_room = models.BooleanField(default=False)
    cooking_in_room = models.BooleanField(default=False)
    fragrance_sensitive = models.BooleanField(default=False)
    music_video = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences of {self.user}"


class RoommateRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_requests"
    )
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevent duplicate requests between the same pair (same direction).
        unique_together = ("sender", "receiver")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"


class Room(models.Model):
    hostel = models.CharField(max_length=120)
    floor = models.SmallIntegerField()
    room_number = models.CharField(max_length=20)
    capacity = models.PositiveSmallIntegerField(default=2)
    available_beds = models.PositiveSmallIntegerField(default=2)

    class Meta:
        unique_together = ("hostel", "room_number")
        ordering = ["hostel", "floor", "room_number"]

    def __str__(self):
        return f"{self.hostel} · {self.room_number} (Floor {self.floor})"
