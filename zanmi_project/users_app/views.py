from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import UserProfileForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from domain.user import User as DomainUser
from services.use_cases import get_profile_detail, create_or_update_user_profile
from .repositories import DjangoUserProfileRepository
from datetime import date


def register_view(request):
    if request.user.is_authenticated:
        return redirect("landing")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            repo = DjangoUserProfileRepository()
            create_or_update_user_profile(
                repo=repo,
                username=user.username,
                user_id=user.id,
                city="",  # or default values
                country="",
                is_certified=False
            )
            login(request, user)
            return redirect("event_detail", event_id=1)  # or secret event
    else:
        form = CustomUserCreationForm()

    return render(request, "users_app/register.html", {"form": form})


@login_required
def profile(request, username=None):
    repo = DjangoUserProfileRepository()
    current_user = DomainUser(username=request.user.username)
    if not username or username == request.user.username:
        target_user = current_user
        target_user_id = request.user.id
        can_edit = True
    else:
        from django.contrib.auth import get_user_model
        UserDB = get_user_model()
        try:
            db_user = UserDB.objects.get(username=username)
            target_user = DomainUser(username=db_user.username)
            target_user_id = db_user.id
            can_edit = False
        except UserDB.DoesNotExist:
            return render(request, "404.html", status=404)
    profile = get_profile_detail(user_id=target_user_id, repo=repo)
    age = profile.get_age(date.today())
    interest_list = [i.strip() for i in profile.centers_of_interest.split(",") if i.strip()]
    upcoming_events = []  # To be replaced with real logic
    past_events = []
    events_attended_count = len(past_events)
    upcoming_events_count = len(upcoming_events)
    return render(request, "users_app/profile.html", {
        "profile": profile,
        "can_edit": can_edit,
        "age": age,
        "interest_list": interest_list,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "events_attended_count": events_attended_count,
        "upcoming_events_count": upcoming_events_count,
    })


@login_required
def profile_edit(request):
    print("PROFILE EDIT")
    repo = DjangoUserProfileRepository()
    current_user = request.user
    domain_user = DomainUser(username=current_user.username)
    domain_profile = get_profile_detail(user_id=current_user.id, repo=repo)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        print("REQUEST FILES IMMEDIATELY AFTER FORM INIT:")
        print(request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            print("request files")
            print(request.FILES.get("avatar"))
            create_or_update_user_profile(
                repo=repo,
                username=current_user.username,
                user_id=current_user.id,
                avatar=request.FILES.get("avatar"),
                city=data["city"],
                description=data["description"],
                country=data["country"],
                birth_date=data.get("birth_date"),
                languages_spoken=data["languages_spoken"],
                centers_of_interest=data["centers_of_interest"],
                event_expectations=data["event_expectations"],
                activity_preferences=data["activity_preferences"],
                group_size_preference=data["group_size_preference"],
                dietary_restrictions=data["dietary_restrictions"],
            )
            return redirect("profile")
    else:
        form = UserProfileForm(initial={
            "city": domain_profile.city,
            "country": domain_profile.country,
            "birth_date": domain_profile.birth_date,
            "description": domain_profile.description,
            "languages_spoken": domain_profile.languages_spoken,
            "centers_of_interest": domain_profile.centers_of_interest,
            "event_expectations": domain_profile.event_expectations,
            "activity_preferences": domain_profile.activity_preferences,
            "group_size_preference": domain_profile.group_size_preference,
            "dietary_restrictions": domain_profile.dietary_restrictions,

        })
    return render(request, "users_app/profile_edit.html", {
        "form": form,
        "profile": domain_profile,
    })