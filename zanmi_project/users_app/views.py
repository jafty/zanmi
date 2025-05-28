from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import UserProfileForm, CustomUserCreationForm, UsernameForm
from django.contrib.auth.decorators import login_required
from domain.user import User as DomainUser
from services.use_cases import get_profile_detail, create_or_update_user_profile, get_upcoming_participations, get_past_participations
from .repositories import DjangoUserProfileRepository
from events_app.repositories import DjangoParticipationRepository, DjangoEventRepository
from datetime import date, datetime
from django.utils.timezone import now


def register_view(request):
    if request.user.is_authenticated:
        return redirect("featured_event") # Redirect to a relevant page

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # Don't save the user yet
            # Handle password saving manually since we took it out of Meta fields
            user.set_password(form.cleaned_data['password1'])
            user.save() # Now save the user

            repo = DjangoUserProfileRepository()
            # Assuming create_or_update_user_profile handles creating the profile if it doesn't exist
            create_or_update_user_profile(
                repo=repo,
                username=user.username,
                user_id=user.id,
                city="",  # or default values
                country="",
                is_certified=False
            )
            now_time = now()
            if form.cleaned_data.get('privacy_policy_consent'):
                profile.privacy_policy_consent = True
                profile.privacy_policy_consent_date = now_time
                profile.privacy_policy_consent_text = "I agree to the processing of my data as outlined in the Privacy Policy." # Store the exact text
            if form.cleaned_data.get('terms_of_service_consent'):
                profile.terms_of_service_consent = True
                profile.terms_of_service_consent_date = now_time
                profile.terms_of_service_consent_text = "I agree to the Terms of Service." # Store the exact text
            if form.cleaned_data.get('event_invitation_consent'):
                profile.event_invitation_consent = True
                profile.event_invitation_consent_date = now_time
                profile.event_invitation_consent_text = "I would like to receive email invitations to events." # Store the exact text
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("profile_edit") # Redirect to profile edit or a welcome page
    else:
        form = CustomUserCreationForm()

    return render(request, "users_app/register.html", {"form": form})

@login_required
def profile(request, username=None):
    repo = DjangoUserProfileRepository()
    participation_repo = DjangoParticipationRepository()
    if not username or username == request.user.username:
        target_user_id = request.user.id
        can_edit = True
    else:
        from django.contrib.auth import get_user_model
        UserDB = get_user_model()
        try:
            db_user = UserDB.objects.get(username=username)
            target_user_id = db_user.id
            can_edit = False
        except UserDB.DoesNotExist:
            return render(request, "404.html", status=404)
    profile = get_profile_detail(user_id=target_user_id, repo=repo)
    age = profile.get_age(date.today())
    interest_list = [i.strip() for i in profile.centers_of_interest.split(",") if i.strip()]
    now = datetime.now()
    event_repo = DjangoEventRepository()
    upcoming_events = get_upcoming_participations(target_user_id, participation_repo, now)
    for event in upcoming_events:
        event.id = event_repo.get_event_id(event)
    past_events = get_past_participations(target_user_id, participation_repo, now)
    for event in past_events:
        event.id = event_repo.get_event_id(event)
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
                perfect_outing_description=data["perfect_outing_description"],
                music_preference=data["music_preference"],
                fun_fact=data["fun_fact"],
                group_size_preference=data["group_size_preference"],
                dietary_restrictions=data["dietary_restrictions"],
            )
            return redirect("featured_event")
    else:
        form = UserProfileForm(initial={
            "city": domain_profile.city,
            "country": domain_profile.country,
            "birth_date": domain_profile.birth_date,
            "description": domain_profile.description,
            "languages_spoken": domain_profile.languages_spoken,
            "centers_of_interest": domain_profile.centers_of_interest,
            "event_expectations": domain_profile.event_expectations,
            "perfect_outing_description": domain_profile.perfect_outing_description,
            "music_preference": domain_profile.music_preference,
            "fun_fact": domain_profile.fun_fact,
            "group_size_preference": domain_profile.group_size_preference,
            "dietary_restrictions": domain_profile.dietary_restrictions,

        })
    return render(request, "users_app/profile_edit.html", {
        "form": form,
        "profile": domain_profile,
    })


@login_required
def post_login_redirect(request):
    print("post login redirect")
    user = request.user
    if user.username.startswith("temp_"):
        return redirect('complete_social_signup')
    return redirect('featured_event')


@login_required
def complete_social_signup(request):
    print("complete social signup")
    user = request.user
    repo = DjangoUserProfileRepository()
    if not user.username.startswith("temp_"):
        create_or_update_user_profile(
            repo=repo,
            username=user.username,
            user_id=user.id,
            city="",  # or default values
            country="",
            is_certified=False
        )
        return redirect('profile_edit')
    if request.method == 'POST':
        form = UsernameForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            create_or_update_user_profile(
                repo=repo,
                username=user.username,
                user_id=user.id,
                city="",  # or default values
                country="",
                is_certified=False
            )
            return redirect('profile_edit')
    else:
        form = UsernameForm(instance=user)
    return render(request, 'users_app/complete_signup.html', {'form': form})
