from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=120, required=True)

    class Meta:
        model = User
        fields = ["username", "full_name", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    """Step 1: identity + hostel/room basics."""

    class Meta:
        model = User
        fields = [
            "full_name", "age", "gender", "college", "branch", "year", "cgpa",
            "hostel", "preferred_floor", "current_floor", "phone", "contact_preference",
        ]
        widgets = {
            "gender": forms.Select(),
            "year": forms.Select(),
            "preferred_floor": forms.Select(),
            "current_floor": forms.Select(),
            "contact_preference": forms.Select(),
        }

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age and (age < 16 or age > 60):
            raise forms.ValidationError("Please enter a realistic age.")
        return age
