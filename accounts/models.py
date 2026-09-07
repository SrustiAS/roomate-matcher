from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user = identity + profile (the 'Users' table from the spec).
    Auth fields (username, email, password) come from AbstractUser.
    Passwords are always stored hashed by Django — never in plain text.
    """

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("na", "Prefer not to say"),
    ]
    YEAR_CHOICES = [
        (1, "1st Year"),
        (2, "2nd Year"),
        (3, "3rd Year"),
        (4, "4th Year"),
        (5, "5th Year / PG"),
    ]
    FLOOR_CHOICES = [
        (0, "Ground Floor"),
        (1, "1st Floor"),
        (2, "2nd Floor"),
        (3, "3rd Floor"),
        (4, "4th Floor"),
        (5, "5th Floor"),
        (-1, "Any Floor"),
    ]
    CONTACT_CHOICES = [
        ("in_app", "In-app only"),
        ("email", "Share email after mutual match"),
        ("phone", "Share phone after mutual match"),
    ]

    full_name = models.CharField(max_length=120, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    college = models.CharField(max_length=150, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Optional. Used only as a soft preference, never as a ranking of worth.",
    )
    hostel = models.CharField(max_length=120, blank=True)
    preferred_floor = models.SmallIntegerField(choices=FLOOR_CHOICES, null=True, blank=True)
    current_floor = models.SmallIntegerField(choices=FLOOR_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)  # private, never public
    contact_preference = models.CharField(
        max_length=10, choices=CONTACT_CHOICES, default="in_app"
    )
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name or self.username

    @property
    def has_preferences(self):
        return hasattr(self, "preferences")

    @property
    def profile_complete(self):
        return bool(self.age and self.branch and self.year and self.hostel)
