# events_app/repositories.py
from domain.event import Event, Participation
from django.contrib.auth import get_user_model
from domain.user import User
from domain.repositories.event_repository import EventRepository
from domain.repositories.participation_repository import ParticipationRepository
from .models import EventDB, ParticipationDB
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
            start_datetime=db_event.start_datetime,
            organizer=organizer,
            price=float(db_event.price),
            description=db_event.description or "",
            time=db_event.time or "",
            activity_type=db_event.activity_type or "",
            image_url=db_event.image.url if db_event.image else ""
        )


class DjangoParticipationRepository(ParticipationRepository):
    def save_participation(self, participation: Participation):
        db_user = UserDB.objects.get(username=participation.user.username)
        db_event = EventDB.objects.get(
            start_datetime=participation.event.start_datetime,
            organizer__username=participation.event.organizer.username
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

    def get_existing_participation(self, user_id: int, event_id: int):
        return ParticipationDB.objects.filter(user_id=user_id, event_id=event_id).first()

    def get_pending_participations(self, event_id):
        return ParticipationDB.objects.filter(event_id=event_id, status="PENDING")
    

# users_app/repositories.py


from domain.user import User


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
