from django.shortcuts import render
from datetime import datetime
from services.events_services import get_event_detail, can_manage
from services.events_queries import get_user_event_status
from .forms import ParticipationForm
from domain.user import User as DomainUser
from .repositories import DjangoEventRepository
from django.contrib.auth.decorators import login_required


def to_domain_user(django_user):
    return DomainUser(username=django_user.username)


@login_required
def event_detail(request, event_id):
    repo = DjangoEventRepository()
    domain_event = get_event_detail(event_id, repo)
    user = to_domain_user(request.user)
    participation = None  
    status = get_user_event_status(user, domain_event, participation)
    form = ParticipationForm()
    return render(request, 'events_app/event_detail.html', {
        "event_id": event_id,
        "event": domain_event,
        "user_status": status,
        "is_accepted": status == "ACCEPTED",
        "is_pending": status == "PENDING",
        "is_rejected": status == "REJECTED",
        "can_manage": can_manage(user, domain_event),
        "is_not_joinable": domain_event.is_past(now=datetime.now()),
        "form": form,
        "pending_participants": [],  # à connecter plus tard
        "unread_notifications_count": 0  # à connecter plus tard si besoin
    })