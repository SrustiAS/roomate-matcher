from django import forms
from .models import Preference


class PreferenceForm(forms.ModelForm):
    """The lifestyle questionnaire. Rendered as selectable cards in the template."""

    class Meta:
        model = Preference
        exclude = ["user", "updated_at"]
        widgets = {
            "sleep_type": forms.RadioSelect(),
            "light_preference": forms.RadioSelect(),
            "study_habit": forms.RadioSelect(),
            "noise_preference": forms.RadioSelect(),
            "cleanliness": forms.RadioSelect(),
            "social_level": forms.RadioSelect(),
            "visitor_preference": forms.RadioSelect(),
            "preferred_room_type": forms.RadioSelect(),
            "preferred_room_location": forms.RadioSelect(),
            "sleep_time": forms.TimeInput(attrs={"type": "time"}),
            "wake_time": forms.TimeInput(attrs={"type": "time"}),
            "quiet_hours": forms.TextInput(attrs={"placeholder": "e.g. 11 PM – 7 AM"}),
        }
