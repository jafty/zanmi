from django.shortcuts import render, redirect
from datetime import datetime
from services.use_cases import accept_participation, get_event_detail, get_profile_detail, is_unrelated_to_event, get_user_participation, get_pending_participations, create_participation
from .forms import ParticipationForm
from domain.user import User as DomainUser
from domain.event import Participation
from .repositories import DjangoEventRepository, DjangoParticipationRepository, DjangoUserProfileRepository
from django.contrib.auth.decorators import login_required
from .stub_payment_gateway import StubPaymentGateway
from .forms import ParticipationForm
from django.views.decorators.http import require_POST


@login_required
def event_detail(request, event_id):
    user = request.user
    print("DOMAIN USER")
    print(user.username)
    domain_user = DomainUser(username=user.username)
    event_repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    event = get_event_detail(event_id, repo=event_repo)
    print("ORGA")
    print(event.organizer.username)
    db_participation = get_user_participation(user.id, event_id, participation_repo)
    if db_participation:
        domain_participation = Participation(
            user=domain_user,
            event=event,
            status=db_participation.status,
            payment_id=db_participation.payment_id,
            message=db_participation.message
        )
    else:
        domain_participation = None
    is_manager = event.is_manageable_by(domain_user)
    if is_manager:
        pending_participants = get_pending_participations(event_id, participation_repo)
    else:
        pending_participants = None
    is_unrelated = is_unrelated_to_event(domain_user, event, [domain_participation] if domain_participation else [])
    form = ParticipationForm()
    return render(request, "events_app/event_detail.html", {
        "event": event,
        "is_manager": is_manager,
        "is_unrelated": is_unrelated,
        "is_accepted": domain_participation.is_accepted() if domain_participation else False,
        "is_rejected": domain_participation.is_rejected() if domain_participation else False,
        "is_pending": domain_participation.is_pending() if domain_participation else False,
        "is_past": event.is_past(datetime.now()),
        "event_id": event_id,
        "pending_participants": pending_participants,
        "form": form,
    })


@login_required
def join_event(request, event_id):
    form = ParticipationForm(request.POST)
    event_repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    if not form.is_valid():
        return redirect("event_detail", event_id=event_id)
    event = get_event_detail(event_id, repo=event_repo)
    domain_user = DomainUser(username=request.user.username)
    existing = get_user_participation(request.user.id, event_id, participation_repo)
    if existing:
        return redirect("event_detail", event_id=event_id)  # Or show a flash message?
    participation = event.add_participation(
        user=domain_user,
        payment_gateway=StubPaymentGateway(),  # Replace later
        message=form.cleaned_data["message"]
    )
    if not participation:
        return render(request, "events_app/payment_failed.html")
    # Save participation
    create_participation(participation, participation_repo)
    return redirect("event_detail", event_id=event_id)


@require_POST
@login_required
def manage_participation(request, event_id):
    action = request.POST.get("action")
    target_user_id = request.POST.get("user_id")
    if not action or not target_user_id:
        return redirect("event_detail", event_id=event_id)
    event_repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    payment_gateway = StubPaymentGateway()
    domain_organizer = DomainUser(username=request.user.username)
    event = get_event_detail(event_id, repo=event_repo)
    if not event.is_manageable_by(domain_organizer):
        return redirect("event_detail", event_id=event_id)
    db_participation = get_user_participation(user_id=target_user_id, event_id=event_id, repo=participation_repo)
    if not db_participation:
        return redirect("event_detail", event_id=event_id)
    domain_user = DomainUser(username=db_participation.user.username)
    domain_participation = Participation(
        user=domain_user,
        event=event,
        status=db_participation.status,
        payment_id=db_participation.payment_id,
        message=db_participation.message
    )
    if action == "accept":
        updated = accept_participation(domain_organizer, domain_participation, payment_gateway)
    elif action == "reject":
        print("Reject to do later")
    else:
        return redirect("event_detail", event_id=event_id)  
    participation_repo.save_participation(updated)
    return redirect("event_detail", event_id=event_id)