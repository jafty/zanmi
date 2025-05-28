from domain.user import User
from domain.user_profile import UserProfile
from domain.event import Event, Participation
from domain.notification import Notification
from domain.repositories.event_repository import EventRepository
from domain.repositories.user_profile_repository import UserProfileRepository
from domain.repositories.participation_repository import ParticipationRepository
from domain.repositories.notification_repository import NotificationRepository

from services.queries import *
from services.use_cases import *


# EVENTS USE CASES
# ----------
class FakePaymentGateway:
    def create_payment(self, user, event, amount_cents):
        return f"fake_payment_for_{user.username}_{event.start_datetime}"


def create_event(
    title,
    location,
    start_datetime,
    organizer,
    description,
    time,
    activity_type,
    price,
    repo,
    image_url=""
):
    event = Event(
        title=title,
        location=location,
        start_datetime=start_datetime,
        organizer=organizer,
        price=price,
        description=description,
        time=time,
        activity_type=activity_type,
        image_url=image_url
    )
    repo.save_event(event)
    return event


def get_event_detail(event_id: int, repo: EventRepository) -> Event:
    return repo.get_event_by_id(event_id)


def accept_participation(organizer: User, participation: Participation, payment_gateway):
    if participation.payment_id and payment_gateway:
        print("Payment ID:" + participation.payment_id)
        payment_gateway.capture(participation.payment_id)
        participation.accept()
        return participation


def reject_participation(organizer: User, participation: Participation, payment_gateway):
    if participation.payment_id and payment_gateway:
        payment_gateway.cancel(participation.payment_id)
    participation.reject()
    return participation


def notify_when_accepted(participation: Participation, notification_gateway, notification_repo):
    message = f" accepted you to {participation.event.title}!"
    notification = Notification(
        recipient=participation.user,
        sender=participation.event.organizer,
        message=message,
        event=participation.event,
    )
    success = notification_gateway.send(notification)
    notification_repo.save_notification(notification)


def notify_when_rejected(participation: Participation, notification_gateway, notification_repo):
    message = f" unfortunately rejected you for  {participation.event.title}. The event might be full, or the organizer estimated that it would not be suitable for you. Your credit card has not been debited."
    notification = Notification(
        recipient=participation.user,
        sender=participation.event.organizer,
        message=message,
        event=participation.event,
    )
    success = notification_gateway.send(notification)
    notification_repo.save_notification(notification)


def notify_when_participant_joins(participation: Participation, notification_gateway, notification_repo):
    print("NOTIFYING")
    message = f" has requested to join {participation.event.title}."
    notification = Notification(
        recipient=participation.event.organizer,
        sender=participation.user,
        message=message,
        event=participation.event,
    )
    success = notification_gateway.send(notification)
    notification_repo.save_notification(notification)


def notify_on_announcement_posted(announcement, notification_gateway, notification_repo, participation_repo):
    event = announcement.event
    participations = participation_repo.get_participations_by_event(event)
    accepted_users = [p.user for p in participations if p.status == "ACCEPTED"]
    recipients = accepted_users + [event.organizer]
    text = f"A message has been posted : << {announcement.content} >>"
    notifs = [
        Notification(
            recipient=recipient,
            sender=None,
            message=text,
            event=event
        )
        for recipient in recipients
    ]
    for n in notifs:
        notification_repo.save_notification(n)
    notification_gateway.send_many(notifs)


def get_user_notifications(user_id: int, notification_repo: NotificationRepository):
    return notification_repo.get_notifications_for_user(user_id)


def is_unrelated_to_event(user: User, event: Event, participations):
    if event.is_manageable_by(user):
        return False
    for participation in participations:
        if participation.user.username == user.username:
            return False
    return True


def get_user_participation(user_id: int, event_id: int, repo: ParticipationRepository) -> Participation | None:
    return repo.get_existing_participation(user_id, event_id)


def get_pending_participations(event_id: int, repo: ParticipationRepository) -> Participation | None:
    return repo.get_pending_participations(event_id)


def get_upcoming_participations(user_id, repo, now):
    participations = repo.get_participations_by_user(user_id)
    return [p.event for p in participations if p.status == "ACCEPTED" and not p.event.is_past(now)]


def get_past_participations(user_id, repo, now):
    participations = repo.get_participations_by_user(user_id)
    return [p.event for p in participations if p.status == "ACCEPTED" and p.event.is_past(now)]


def create_participation(participation: Participation, repo: ParticipationRepository) -> Participation | None:
    return repo.save_participation(participation)

# USER PROFILE USE CASES
# ----------
def get_profile_detail(user_id: int, repo: UserProfileRepository):
    return repo.get_by_user_id(user_id)


def create_or_update_user_profile(
    repo: UserProfileRepository,
    username: str,
    city: str = "",
    user_id: str = "",
    country: str = "",
    description: str = "",
    birth_date=None,
    languages_spoken: str = "",
    centers_of_interest: str = "",
    event_expectations: str = "",
    perfect_outing_description: str = "",
    music_preference: str = "",
    fun_fact: str = "",
    group_size_preference: str = "",
    dietary_restrictions: str = "",
    avatar=None,
    is_certified: bool = False,
) -> UserProfile:
    try:
        existing_profile = repo.get_by_user_id(user_id)
    except ValueError:
        existing_profile = UserProfile(
            user=User(username=username, id=user_id),
            city=city,
            country=country,
            birth_date=birth_date,
            is_certified=is_certified,
        )
    existing_profile.user.username = username
    existing_profile.city = city
    existing_profile.country = country
    if birth_date:
        existing_profile.birth_date = birth_date
    existing_profile.languages_spoken = languages_spoken
    existing_profile.description = description
    existing_profile.centers_of_interest = centers_of_interest
    existing_profile.event_expectations = event_expectations
    existing_profile.perfect_outing_description = perfect_outing_description
    existing_profile.music_preference = music_preference
    existing_profile.fun_fact = fun_fact
    existing_profile.group_size_preference = group_size_preference
    existing_profile.dietary_restrictions = dietary_restrictions
    existing_profile.is_certified = is_certified
    if avatar:
        existing_profile.avatar = avatar

    repo.save_user_profile(existing_profile)
    return existing_profile

