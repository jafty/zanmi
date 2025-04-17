from domain.user import User
from domain.user_profile import UserProfile
from domain.event import Event, Participation
from domain.repositories.event_repository import EventRepository
from domain.repositories.user_profile_repository import UserProfileRepository
from domain.repositories.participation_repository import ParticipationRepository

from services.queries import *
from services.use_cases import *


# EVENTS USE CASES
# ----------
class FakePaymentGateway:
    def create_payment(self, user, event, amount_cents):
        return f"fake_payment_for_{user.username}_{event.start_datetime}"


def create_event(
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
        payment_gateway.capture(participation.payment_id)
        participation.accept()
        return participation


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
    activity_preferences: str = "",
    group_size_preference: str = "",
    dietary_restrictions: str = "",
    avatar = None,
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
        existing_profile.activity_preferences = activity_preferences
        existing_profile.group_size_preference = group_size_preference
        existing_profile.dietary_restrictions = dietary_restrictions
        existing_profile.is_certified = is_certified
        if avatar:
            existing_profile.avatar = avatar
        print("EXISTING PROFILE")
        print(existing_profile.description)
        repo.save_user_profile(existing_profile)
        return existing_profile
