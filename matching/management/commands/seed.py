"""Populate the DB with demo students so matching works immediately.
Run: python manage.py seed
Login for any seeded student: username as printed, password 'pass12345'.
"""
import random
from datetime import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from matching.models import Preference, Room

User = get_user_model()

BRANCHES = ["CSE", "ECE", "Mechanical", "Civil", "IT"]
NAMES = ["Ananya", "Rahul", "Priya", "Arjun", "Sneha", "Karan", "Divya", "Vikram",
         "Meera", "Rohit", "Isha", "Aditya"]


class Command(BaseCommand):
    help = "Seed demo students, preferences and rooms."

    def handle(self, *args, **opts):
        random.seed(7)
        created = 0
        for i, name in enumerate(NAMES):
            username = name.lower()
            if User.objects.filter(username=username).exists():
                continue
            u = User.objects.create_user(
                username=username, password="pass12345",
                email=f"{username}@campus.edu", full_name=name,
                age=random.randint(18, 23), gender=random.choice(["male", "female"]),
                college="Campus Institute of Technology",
                branch=random.choice(BRANCHES), year=random.randint(1, 4),
                cgpa=round(random.uniform(6.5, 9.5), 2),
                hostel="Nalanda Hostel",
                preferred_floor=random.choice([0, 1, 2, 3, 3, 3, -1]),
                contact_preference="in_app",
                phone=f"90000000{i:02d}",
            )
            sleep_type = random.choice(["night_owl", "early_bird"])
            if sleep_type == "night_owl":
                st, wt = time(random.choice([0, 1]), 0), time(random.choice([8, 9]), 0)
            else:
                st, wt = time(22, 30), time(random.choice([5, 6]), 0)
            Preference.objects.create(
                user=u, sleep_type=sleep_type, sleep_time=st, wake_time=wt,
                quiet_hours="11 PM – 7 AM",
                light_preference=random.choice(["off", "dim", "dont_mind", "on_study"]),
                study_habit=random.choice(["room", "library", "late_night", "early_morning"]),
                noise_preference=random.choice(["quiet", "moderate", "dont_mind"]),
                cleanliness=random.choice(["very", "moderate", "relaxed"]),
                social_level=random.choice(["very", "moderate", "private"]),
                visitor_preference=random.choice(["none", "occasional", "okay"]),
            )
            created += 1

        for floor in range(0, 4):
            for r in range(1, 4):
                Room.objects.get_or_create(
                    hostel="Nalanda Hostel", room_number=f"{floor}0{r}",
                    defaults={"floor": floor, "capacity": 2, "available_beds": 2},
                )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} students (password: pass12345) + rooms."))
