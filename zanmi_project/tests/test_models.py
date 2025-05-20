import sys
import os
import pytest
from domain.event import Event, Participation, Announcement
from domain.user import User
from domain.user_profile import UserProfile
from datetime import datetime, timezone, date
from unittest.mock import patch

@pytest.fixture
def  organizer():
    organizer = User(username="Host")
    return organizer


@pytest.fixture
def current_date():
    current_date= datetime(2025, 4, 11)
    return current_date


@pytest.fixture
def event():
    user = User("Alice")
    event_date = datetime(2025, 4, 11)
    organizer = User("Host")
    event = Event(title="Sortie", location="Toulouse", start_datetime=event_date, organizer=organizer, price=25.0)
    return event


@pytest.fixture
def participant():
    user = User(username="Alice")
    return user

class StubPaymentGateway:
    def create_payment(self, user, event, amount_in_cents, message=None):
        self.user = user
        self.event = event
        self.amount_in_cents = amount_in_cents
        self.message = message
        return "stub_payment_id"

    def capture(self, payment_id):
        pass


class StubFailedPaymentGateway:
    def create_payment(self, user, event, amount_in_cents):
        return None

    def capture(self, payment_id):
        pass


class StubAnnouncementRepository:
    def __init__(self, announcement1=None, announcement2=None):
        self.saved_announcement = None
        self.announcements = [announcement1, announcement2]

    def save_announcement(self, announcement):
        self.saved_announcement = announcement

    def get_announcements(self, event_title):
        return self.announcements


# EVENT ENTITY
# ----------
def test_event_is_not_past_if_today(event, current_date):
    assert event.is_past(current_date) is False


def test_event_is_not_past_if_in_future(event):
    a_date_before = datetime(2025, 4, 10)
    assert event.is_past(a_date_before) is False


def test_event_is_past_if_in_past(event):
    a_date_after = datetime(2025, 4, 12)
    assert event.is_past(a_date_after) is True


def test_user_joins_event_and_gets_to_pay(participant, event):
    payment_gateway = StubPaymentGateway()
    payment_id = event.checkout_user(
        user=participant,
        payment_gateway=payment_gateway,
        message="Looking forward to it!"
    )
    assert payment_id == "stub_payment_id"
    assert payment_gateway.user == participant
    assert payment_gateway.event == event
    assert payment_gateway.message == "Looking forward to it!"


def test_publish_announcement_by_host(event, organizer):
    repo = StubAnnouncementRepository()
    announcement = event.publish_announcement(
        content="Bienvenue à tous !",
        is_host_message=True,
        announcement_repo=repo,
    )
    assert isinstance(announcement, Announcement)
    assert announcement in event.announcements
    assert announcement.is_host_message is True
    assert repo.saved_announcement == announcement


def test_publish_announcement_by_participant(event, participant):
    repo = StubAnnouncementRepository()
    announcement = event.publish_announcement(
        content="Salut tout le monde, hâte de vous rencontrer !",
        is_host_message=False,
        announcement_repo=repo,
    )
    assert isinstance(announcement, Announcement)
    assert announcement in event.announcements
    assert announcement.is_host_message is False
    assert repo.saved_announcement == announcement


def test_get_announcements_for_event(event):
    announcement1 = Announcement(
        event=event,
        content="Msg #1",
        is_host_message=True
    )
    announcement2 = Announcement(
        event=event,
        content="Msg #2",
        is_host_message=False
    )
    repo = StubAnnouncementRepository(announcement1, announcement2)
    event_announcements = event.get_announcements(
        announcement_repo=repo,
    )
    assert event_announcements == [announcement1, announcement2]


def test_user_joins_waitlist(participant, event):
    participation = event.add_participation(
        user=participant,
        message="Looking forward to it!",
    )
    assert isinstance(participation, Participation)
    assert participation.user == participant
    assert participation.event == event
    assert participation.status == "PENDING"
    assert participation.message == "Looking forward to it!"


def test_created_event_has_default_image(event):
    assert event.image_url == "event_images/event_default.png"


# PARTICIPATION ENTITY
# ----------
def test_user_status_is_accepted(participant: User, event: Event):
    participation = Participation(user=participant, event=event, status="ACCEPTED")
    assert participation.is_accepted()


def test_user_status_is_not_accepted(participant: User, event: Event):
    participation = Participation(user=participant, event=event, status="REJECTED")
    assert not participation.is_accepted()


def test_user_status_is_pending(participant, event):
    participation = Participation(user=participant, event=event, status="PENDING")
    assert participation.is_pending()


def test_user_status_is_not_pending(participant, event):
    participation = Participation(user=participant, event=event, status="ACCEPTED")
    assert not participation.is_pending()


def test_user_status_is_rejected(participant, event):
    participation = Participation(user=participant, event=event, status="REJECTED")
    assert participation.is_rejected()


def test_user_status_is_not_rejected(participant, event):
    participation = Participation(user=participant, event=event, status="PENDING")
    assert not participation.is_rejected()


def test_user_status_is_organizer():
    organizer = User(username="Host")
    event = Event(title="Sortie", location="Toulouse", organizer=User(username="Host"), start_datetime=datetime(2025,4,16))

    status = event.is_manageable_by(organizer)
    assert status == True


def test_user_status_is_not_organizer(participant, event):
    status = event.is_manageable_by(participant)
    assert status == False


# USER PROFILE ENTITY
# ----------
# USERS AGGREGATE
# ----------
def test_user_profile_creation():
    """
    GIVEN a domain User object
    WHEN we create a UserProf ile with various fields
    THEN all fields should be set correctly in-memory, with no DB involved.
    """
    user = User(username="john_doe")
    profile = UserProfile(
        user=user,
        avatar="avatars/custom.jpg",
        description="I love traveling!",
        birth_date=date(1990, 5, 21),
        city="Paris",
        country="France",
        languages_spoken="French, English",
        centers_of_interest="Cooking, Painting",
        event_expectations="Meeting new friends",
        activity_preferences="Sports, Food tours",
        group_size_preference="Medium",
        dietary_restrictions="Vegetarian",
        is_certified=True,
        consent_date=datetime(2025, 1, 10, 14, 30),
        # If you want to test slug generation logic, you can skip passing `slug`
        # or pass an explicit slug. This is purely domain logic, not DB-based.
        slug="john_doe_slug"
    )
    assert profile.user == user
    assert profile.avatar == "avatars/custom.jpg"
    assert profile.description == "I love traveling!"
    assert profile.birth_date == date(1990, 5, 21)
    assert profile.city == "Paris"
    assert profile.country == "France"
    assert profile.languages_spoken == "French, English"
    assert profile.centers_of_interest == "Cooking, Painting"
    assert profile.event_expectations == "Meeting new friends"
    assert profile.activity_preferences == "Sports, Food tours"
    assert profile.group_size_preference == "Medium"
    assert profile.dietary_restrictions == "Vegetarian"
    assert profile.is_certified is True
    assert profile.consent_date == datetime(2025, 1, 10, 14, 30)


def test_user_profile_creation_without_avatar():
    """
    GIVEN a domain User object
    WHEN we create a UserProf ile with various fields
    THEN all fields should be set correctly in-memory, with no DB involved.
    """
    user = User(username="john_doe")
    profile = UserProfile(
        user=user,
        description="I love traveling!",
        birth_date=date(1990, 5, 21),
        city="Paris",
        country="France",
        languages_spoken="French, English",
        centers_of_interest="Cooking, Painting",
        event_expectations="Meeting new friends",
        activity_preferences="Sports, Food tours",
        group_size_preference="Medium",
        dietary_restrictions="Vegetarian",
        is_certified=True,
        consent_date=datetime(2025, 1, 10, 14, 30),
        # If you want to test slug generation logic, you can skip passing `slug`
        # or pass an explicit slug. This is purely domain logic, not DB-based.
        slug="john_doe_slug"
    )
    assert profile.user == user
    assert profile.avatar == "avatars/default.jpg"
    assert profile.description == "I love traveling!"
    assert profile.birth_date == date(1990, 5, 21)
    assert profile.city == "Paris"
    assert profile.country == "France"
    assert profile.languages_spoken == "French, English"
    assert profile.centers_of_interest == "Cooking, Painting"
    assert profile.event_expectations == "Meeting new friends"
    assert profile.activity_preferences == "Sports, Food tours"
    assert profile.group_size_preference == "Medium"
    assert profile.dietary_restrictions == "Vegetarian"
    assert profile.is_certified is True
    assert profile.consent_date == datetime(2025, 1, 10, 14, 30)


def test_can_edit_own_profile(participant):
    """
    GIVEN a UserProfile that belongs to a specific user
    WHEN we call can_edit() with that same user
    THEN it should return True
    """
    profile = UserProfile(user=participant, description="Participant's profile")
    # make sure that we test two different objects since it will happen
    result = profile.can_edit(User(username=participant.username))
    assert result is True


def test_cannot_edit_other_users_profile(participant):
    """
    GIVEN a UserProfile that belongs to a specific user
    WHEN we call can_edit() with a different user
    THEN it should return False
    """
    stranger = User(username="stranger_user")
    profile = UserProfile(user=participant, description="Owner's profile")
    result = profile.can_edit(stranger)
    assert result is False


def test_get_age_returns_correct_age_35(participant):
    """
    GIVEN a UserProfile with a birth_date of 1990-05-21
    WHEN we ask for the age on 2025-05-21
    THEN it should return 35
    """
    birth_date = date(1990, 5, 21)
    profile = UserProfile(user=participant, birth_date=birth_date)
    today = date(2025, 5, 21)
    age = profile.get_age(today)
    assert age == 35


def test_get_age_returns_correct_age_36(participant):
    """
    GIVEN a UserProfile with a birth_date of 1990-05-21
    WHEN we ask for the age on 2025-05-21
    THEN it should return 35
    """
    birth_date = date(1989, 5, 21)
    profile = UserProfile(user=participant, birth_date=birth_date)
    today = date(2025, 5, 21)
    age = profile.get_age(today)
    assert age == 36


def test_get_age_returns_correct_age_29(participant):
    """
    GIVEN a UserProfile with a birth_date of 1990-05-21
    WHEN we ask for the age on 2025-05-21
    THEN it should return 35
    """
    birth_date = date(1995, 9, 19)
    profile = UserProfile(user=participant, birth_date=birth_date)
    today = date(2025, 5, 21)
    age = profile.get_age(today)
    assert age == 29


def test_get_age_is_none_when_no_birth_date(participant):
    """
    GIVEN a UserProfile with a birth_date of 1990-05-21
    WHEN we ask for the age on 2025-05-21
    THEN it should return 35
    """
    profile = UserProfile(user=participant)
    today = date(2025, 5, 21)
    age = profile.get_age(today)
    assert age == None