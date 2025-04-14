from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("event_detail", event_id=1)  # or secret event
    else:
        form = CustomUserCreationForm()

    return render(request, "users_app/register.html", {"form": form})
