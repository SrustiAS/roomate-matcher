from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProfileForm, SignUpForm


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "landing.html")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.full_name = form.cleaned_data["full_name"]
            user.save()
            login(request, user)
            messages.success(request, "Welcome! Let's set up your profile.")
            return redirect("profile_setup")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def profile_setup(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved. Now the lifestyle questionnaire.")
            return redirect("questionnaire")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_setup.html", {"form": form})


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile_user": request.user})
