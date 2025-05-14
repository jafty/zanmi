# events_app/repositories.py
from domain.event import Event, Participation
from domain.notification import Notification
from django.contrib.auth import get_user_model
from domain.user import User
from domain.repositories.event_repository import EventRepository
from domain.repositories.participation_repository import ParticipationRepository
from domain.repositories.notification_repository import NotificationRepository
from .models import EventDB, ParticipationDB, NotificationDB
from users_app.models import UserProfileDB
from domain.user_profile import UserProfile
from domain.user import User
from domain.repositories.user_profile_repository import UserProfileRepository


UserDB = get_user_model()

class DjangoEventRepository(EventRepository):

    def save_event(self, event: Event) -> None:
        if hasattr(event, 'id') and event.id:  # if domain has an id
            db_event = EventDB.objects.get(id=event.id)
        else:
            db_event = EventDB()
        db_event.start_datetime = event.start_datetime
        db_event.organizer_id = event.organizer.id  # domain user has .id
        db_event.price = event.price
        db_event.description = event.description
        db_event.time = event.time
        db_event.activity_type = event.activity_type
        db_event.image_url = event.image_url
        db_event.save()

    def get_event_by_id(self, event_id: int) -> Event:
        db_event = EventDB.objects.get(id=event_id)
        organizer = User(username=db_event.organizer.username)
        return Event(
            title=db_event.title,
            location=db_event.location,
            start_datetime=db_event.start_datetime,
            organizer=organizer,
            price=float(db_event.price),
            description=db_event.description or "",
            time=db_event.time or "",
            activity_type=db_event.activity_type or "",
            image_url=db_event.image.url if db_event.image else ""
        )

    def get_event_id(self, event: Event) -> id:
        db_event = EventDB.objects.get(title=event.title)
        return db_event.id


class DjangoParticipationRepository(ParticipationRepository):

    def save_participation(self, participation: Participation) -> Participation:
        db_user = UserDB.objects.get(username=participation.user.username)
        db_event = EventDB.objects.get(
            title=participation.event.title,
        )
        ParticipationDB.objects.update_or_create(
            user=db_user,
            event=db_event,
            defaults={
                "status": participation.status,
                "payment_id": participation.payment_id,
                "message": participation.message
            }
        )
        return participation

    def get_existing_participation(self, user_id: int, event_id: int):
        return ParticipationDB.objects.filter(user_id=user_id, event_id=event_id).first()

    def get_pending_participations(self, event_id):
        return ParticipationDB.objects.filter(event_id=event_id, status="PENDING")

    def get_participations_by_user(self, user_id: int) -> list[Participation]:
        db_participations = ParticipationDB.objects.select_related("event", "event__organizer").filter(user_id=user_id)
        return [
            Participation(
                user=User(username=p.user.username),
                event=Event(
                    title=p.event.title,
                    location=p.event.location,
                    start_datetime=p.event.start_datetime,
                    organizer=User(username=p.event.organizer.username),
                    price=p.event.price,
                    image_url=p.event.image.url if p.event.image else ""
                ),
                status=p.status,
                payment_id=p.payment_id,
                message=p.message
            )
            for p in db_participations
        ]


class DjangoUserProfileRepository(UserProfileRepository):

    def get_by_user_id(self, user_id: int) -> UserProfile:
        db_profile = UserProfileDB.objects.get(user_id=user_id)
        return UserProfile(
            user=User(username=db_profile.user.username, id=db_profile.user.id),
            avatar=db_profile.avatar.url if db_profile.avatar else "avatars/default.jpg",
            description=db_profile.description,
            birth_date=db_profile.birth_date,
            city=db_profile.city,
            country=db_profile.country,
            languages_spoken=db_profile.languages_spoken,
            centers_of_interest=db_profile.centers_of_interest,
            event_expectations=db_profile.event_expectations,
            activity_preferences=db_profile.activity_preferences,
            group_size_preference=db_profile.group_size_preference,
            dietary_restrictions=db_profile.dietary_restrictions,
            is_certified=db_profile.is_certified,
            consent_date=db_profile.consent_date,
            slug=db_profile.slug,
        )

    def save_user_profile(self, user_profile: UserProfile) -> None:
        from django.contrib.auth import get_user_model
        UserDB = get_user_model()
        user = UserDB.objects.get(id=user_profile.user.id)
        obj, _ = UserProfileDB.objects.get_or_create(user=user)

        obj.description = user_profile.description
        obj.birth_date = user_profile.birth_date
        obj.city = user_profile.city
        obj.country = user_profile.country
        obj.languages_spoken = user_profile.languages_spoken
        obj.centers_of_interest = user_profile.centers_of_interest
        obj.event_expectations = user_profile.event_expectations
        obj.activity_preferences = user_profile.activity_preferences
        obj.group_size_preference = user_profile.group_size_preference
        obj.dietary_restrictions = user_profile.dietary_restrictions
        obj.is_certified = user_profile.is_certified
        obj.save()


class DjangoNotificationRepository(NotificationRepository):

    def save_notification(self, notification: Notification) -> None:
        recipient = UserDB.objects.get(username=notification.recipient.username)
        sender = UserDB.objects.get(username=notification.sender.username)
        db_event = EventDB.objects.get(
            title=notification.event.title,
        )
        NotificationDB.objects.create(
            recipient=recipient,
            sender=sender,
            message=notification.message,
            event=db_event
        )

    def count_unread_notifications(self, user_id: int) -> int:
        return NotificationDB.objects.filter(recipient_id=user_id, is_read=False).count()

    def get_notifications_for_user(self, user_id: int) -> list[Notification]:
        db_notifications = NotificationDB.objects.filter(recipient_id=user_id).order_by("-created_at")
        return [
            Notification(
                recipient=User(username=n.recipient.username),
                sender=User(username=n.sender.username),
                message=n.message,
                event=Event(
                    title=n.event.title,
                    location=n.event.location,
                    start_datetime=n.event.start_datetime,
                    organizer=User(username=n.event.organizer.username),
                    image_url = n.event.image.url if n.event.image else "",
                ),
            )
            for n in db_notifications
        ]

    def mark_all_as_read(self, user_id: int):
        NotificationDB.objects.filter(recipient_id=user_id, is_read=False).update(is_read=True)

