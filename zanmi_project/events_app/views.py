from django.shortcuts import render, redirect
from datetime import datetime
from services.events_services import join_event, get_event_detail, can_manage
from services.events_queries import get_user_event_status
from .forms import ParticipationForm
from domain.user import User as DomainUser
from .repositories import DjangoEventRepository, DjangoParticipationRepository
from django.contrib.auth.decorators import login_required


def to_domain_user(django_user):
    return DomainUser(username=django_user.username)


class FakePaymentGateway:
    def create_payment(self, user, event, amount_cents):
        # Dans une vraie intégration, tu appellerais Stripe ou autre ici
        return f"fake_payment_for_{user.username}_{event.start_datetime.strftime('%Y%m%d')}"


@login_required
def event_detail(request, event_id):
    repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    domain_event = get_event_detail(event_id, repo)
    domain_user = DomainUser(username=request.user.username)
    form = ParticipationForm()
    if request.method == "POST":
        form = ParticipationForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data.get("message", "")
            existing = participation_repo.get_existing_participation(request.user.id, event_id)

            if not existing:
                participation = join_event(
                    user=domain_user,
                    event=domain_event,
                    existing_participations=[],  # Tu pourras remplacer ça plus tard
                    payment_gateway=FakePaymentGateway(),
                    message=message
                )
                participation_repo.save_participation(participation)
                return redirect("event_detail", event_id=event_id)

    # Get updated status (e.g. accepted, rejected, etc.)
    participation = participation_repo.get_existing_participation(request.user.id, event_id)
    status = get_user_event_status(domain_user, domain_event, participation)

    return render(request, 'events_app/event_detail.html', {
        "event_id": event_id,
        "event": domain_event,
        "user_status": status,
        "is_accepted": status == "ACCEPTED",
        "is_pending": status == "PENDING",
        "is_rejected": status == "REJECTED",
        "can_manage": can_manage(domain_user, domain_event),
        "is_not_joinable": domain_event.is_past(now=datetime.now()),
        "form": form,
        "pending_participants": [],  # À connecter si besoin
        "unread_notifications_count": 0  # Idem
    })