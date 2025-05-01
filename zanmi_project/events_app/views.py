from django.shortcuts import render, redirect
from datetime import datetime
from .stripe_payment_gateway import StripePaymentGateway
from services.use_cases import (
    accept_participation,
    get_event_detail,
    get_profile_detail,
    is_unrelated_to_event,
    notify_when_accepted,
    get_user_participation,
    get_pending_participations,
    create_participation,
    notify_when_rejected,
    notify_when_participant_joins,
    accept_participation,
    reject_participation,
    get_user_notifications,
)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import ParticipationForm
from domain.user import User as DomainUser
from domain.event import Participation
from .repositories import DjangoEventRepository, DjangoParticipationRepository, DjangoUserProfileRepository, DjangoNotificationRepository
from django.contrib.auth.decorators import login_required
from .email_notification_gateway import EmailNotificationGateway
from .forms import ParticipationForm
from django.contrib.auth import get_user_model
UserDB = get_user_model()
from events_app.models import EventDB
from django.views.decorators.http import require_POST
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def landing(request):
    return render(request, 'events_app/landing.html')


login_required
def featured_event(request):
    return redirect('event_detail', event_id=3)


@login_required
def event_detail(request, event_id):
    user = request.user
    domain_user = DomainUser(username=user.username)
    event_repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    event = get_event_detail(event_id, repo=event_repo)
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
        "location": event.location,
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
        return redirect("event_detail", event_id=event_id)  # Optional: add flash message
    payment_gateway = StripePaymentGateway()
    payment_id = event.checkout_user(
        user=domain_user,
        payment_gateway=payment_gateway,
        message=form.cleaned_data["message"]
    )
    if not payment_id:
        return render(request, "events_app/payment_failed.html")
    return redirect(payment_id)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        stripe_event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({"error": "Invalid webhook"}, status=400)
    if stripe_event['type'] == "checkout.session.completed":
        session = stripe_event['data']['object']
        username = session['metadata']['username']
        event_title = session['metadata']['event_title']
        message = session['metadata'].get('message', '')
        payment_intent_id = session['payment_intent']
        event_db = EventDB.objects.get(title=event_title)
        domain_user = DomainUser(username=username)
        domain_event = DjangoEventRepository().get_event_by_id(event_db.id)
        participation = domain_event.add_participation(
            user=domain_user,
            message=message
        )
        participation.payment_id = payment_intent_id
        participation_repo = DjangoParticipationRepository()
        notification_gateway = EmailNotificationGateway()
        notification_repo = DjangoNotificationRepository()
        created = create_participation(participation, participation_repo)
        notify_when_participant_joins(created, notification_gateway, notification_repo)
    return JsonResponse({"status": "success"})


login_required
def stripe_success(request):
    return render(request, 'events_app/stripe_success.html')

login_required
def stripe_cancel(request):
    return render(request, 'events_app/stripe_cancel.html')


@require_POST
@login_required
def manage_participation(request, event_id):
    action = request.POST.get("action")
    target_user_id = request.POST.get("user_id")
    if not action or not target_user_id:
        return redirect("event_detail", event_id=event_id)
    event_repo = DjangoEventRepository()
    participation_repo = DjangoParticipationRepository()
    notification_repo = DjangoNotificationRepository()
    payment_gateway =StripePaymentGateway()  
    notification_gateway = EmailNotificationGateway()  #TODO : send email
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
        notify_when_accepted(updated, notification_gateway, notification_repo)
    elif action == "reject":
        updated = reject_participation(domain_organizer, domain_participation, payment_gateway)
        notify_when_rejected(updated, notification_gateway, notification_repo)
    else:
        return redirect("event_detail", event_id=event_id)
    participation_repo.save_participation(updated)
    return redirect("event_detail", event_id=event_id)


@login_required
def notifications_view(request):
    user = request.user
    user_id = user.id
    domain_user = DomainUser(username=user.username)
    notification_repo = DjangoNotificationRepository()
    event_repo = DjangoEventRepository()
    notifications = get_user_notifications(user_id=user_id, notification_repo=notification_repo)
    for notification in notifications:
        notification.event.id = event_repo.get_event_id(notification.event)
    notification_repo.mark_all_as_read(user_id)
    return render(request, "events_app/notifications.html", {
        "notifications": notifications
    })
