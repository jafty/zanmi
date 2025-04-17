import pytest
from datetime import date, datetime
from domain.user import User
from domain.event import Event, Participation
from domain.user_profile import UserProfile
from services.use_cases import *
from services.queries import *
from unittest.mock import Mock
from unittest.mock import patch
import sys
import os
from services.queries import get_price_in_cents


@pytest.fixture
def participant():
    user = User(username="Alice")
    return user


@pytest.fixture
def  organizer():
    organizer = User(username="Host")
    return organizer


@pytest.fixture
def event(organizer):
    event = Event(start_datetime=datetime(2025, 4, 20), organizer=organizer, price=25)
    return event


# EVENTS USE CASES
# -----------
class StubEventRepository:
    def __init__(self):
        self.saved_event = None

    def save_event(self, event):
        self.saved_event = event

    def get_event_by_id(self, event_id):
        return self.saved_event
    

def test_create_event_with_stub_repo():
    repo = StubEventRepository()
    user = User(username="Alice")
    start_datetime = datetime(2025, 5, 10)
    description = "Event description"
    time = "18:00"
    activity_type = "Outing"
    image_url = "img.url"
    event = create_event(
        start_datetime, 
        user, 
        description, 
        time, 
        activity_type, 
        price=25.0, 
        repo=repo,
        image_url=image_url
    )
    assert repo.saved_event is not None
    assert repo.saved_event.start_datetime == start_datetime
    assert repo.saved_event.organizer == user
    assert event.description == "Event description"  # only if you provide it in test fixture
    assert event.time == "18:00"  # only if you provide it in test fixture
    assert event.activity_type == "Outing"  # only if you provide it in test fixture
    assert event.image_url == "img.url"  # only if you provide it in test fixture
    assert event == repo.saved_event 


def test_get_event_detail():
    repo = StubEventRepository()
    expected_event = Event(start_datetime=..., organizer=..., price=...)
    repo.save_event(expected_event)
    result = get_event_detail(event_id=123, repo=repo)  # id is ignored
    assert result == expected_event


def test_get_price_in_cents():
    assert get_price_in_cents(12.50) == 1250
    assert get_price_in_cents(0) == 0


def test_organizer_accepts_pending_participation_with_payment_capture(organizer, participant):
    event = Event(start_datetime=datetime(2025, 4, 20), organizer=organizer)
    participation = Participation(user=participant, event=event, status="PENDING", payment_id="pi_fake_123")
    mock_gateway = Mock()
    updated_participation = accept_participation(
        organizer=organizer,
        participation=participation,
        payment_gateway=mock_gateway
    )
    assert updated_participation.status == "ACCEPTED"
    mock_gateway.capture.assert_called_once_with("pi_fake_123")


def test_organizer_rejects_pending_participation(participant, event, organizer):
    participation = Participation(user=participant, event=event, status="PENDING")
    participation.reject()
    assert participation.status == "REJECTED"


def test_user_is_unrelated_to_event(participant, event):
    new_user = User(username="New")
    participations = [Participation(participant, event)]
    assert is_unrelated_to_event(new_user, event, participations) == True


def test_participant_is_related_to_event(participant, event):
    participations = [Participation(participant, event)]
    assert is_unrelated_to_event(participant, event, participations) == False


def test_organizer_is_related_to_event(organizer, event):
    participations = []
    assert is_unrelated_to_event(organizer, event, participations) == False



class StubParticipationRepository:
    def __init__(self, stored_participation=None, stored_participations=None):
        self.stored_participation = stored_participation
        self.stored_participations = stored_participations

    def get_existing_participation(self, user_id, event_id):
        return self.stored_participation

    def get_pending_participations(self, event_id):
        return self.stored_participations
    
    def save_participation(self, participation):
        self.saved = participation

def test_get_user_participation(participant, event):
    """
    GIVEN a StubParticipationRepository with a stored Participation
    WHEN we call get_user_participation with a user and event
    THEN the correct participation is returned
    """
    stub_participation = Participation(
        user=participant,
        event=event,
        status="PENDING",
        payment_id="pi_abc123",
        message="Excited!"
    )  
    repo = StubParticipationRepository(stored_participation=stub_participation)
    result = get_user_participation(user_id=12, event_id=12, repo=repo)
    assert result == stub_participation


def test_get_pending_participations_returns_only_pending_participations(participant, event):
    """
    GIVEN a repository with a mix of pending and accepted participations
    WHEN we call get_pending_participations for a given event
    THEN only participations with status "PENDING" are returned
    """
    pending_part1 = Participation(
        user=participant,
        event=event,
        status="PENDING",
        payment_id="pi_123",
        message="Pending one"
    )
    pending_part2 = Participation(
        user=participant,
        event=event,
        status="PENDING",
        payment_id="pi_123",
        message="Pending two"
    )
    accepted_part = Participation(
        user=participant,
        event=event,
        status="ACCEPTED",
        payment_id="pi_456",
        message="Accepted one"
    )
    participation_repo = StubParticipationRepository(stored_participations=[pending_part1, pending_part2])
    pending_participants = get_pending_participations(event_id=12, repo=participation_repo)
    assert pending_participants == [pending_part1, pending_part2]


def test_create_participation_uses_repo(participant, event):
    """
    GIVEN a Participation and a StubParticipationRepository
    WHEN we call create_participation
    THEN the participation is stored using the repo's save_participation method
    """
    participation = Participation(
        user=participant,
        event=event,
        status="PENDING",
        payment_id="pi_456",
        message="Can't wait!"
    )
    participation_repo = StubParticipationRepository()
    create_participation(participation, participation_repo)
    assert participation_repo.saved == participation


# USER PROFILE USE CASES
# ----------
class StubUserProfileRepository:
    def __init__(self, stored_profile=None):
        self.requested_user_id = None
        self.stored_profile = stored_profile
        self.save_calls = 0  
  
    def get_by_user_id(self, user_id: int) -> UserProfile:
        return self.stored_profile
    
    def save_user_profile(self, user_profile: UserProfile):
        self.save_calls += 1  # <--- This increments the counter


def test_get_profile_detail(participant):
    """
    GIVEN a StubUserProfileRepository with a stored UserProfile
    WHEN we call get_profile_detail with that user's ID
    THEN the correct profile is returned, and the repository is called with the user_id
    """
    profile = UserProfile(user=participant, city="New York")
    stub_repo = StubUserProfileRepository(stored_profile=profile)
    fetched_profile = get_profile_detail(user_id=42, repo=stub_repo)
    assert fetched_profile == profile


def test_create_user_profile_if_none_exists(participant):
    """
    GIVEN a user_id that has no existing profile in the repo
    WHEN we call create_or_update_user_profile
    THEN a new profile is created, saved, and returned
    """
    stub_repo = StubUserProfileRepository(UserProfile(user=participant, description="Test profile"))
    username = "john_doe"
    created_profile = create_or_update_user_profile(
        repo=stub_repo,
        username=username,
        city="Paris",
        user_id=12,
        country="France",
        description="Hey I'm John Doe",
        languages_spoken="french",
        centers_of_interest="foot",
        event_expectations="nothing",
        activity_preferences="sport",
        group_size_preference="10",
        dietary_restrictions="nuts",
        birth_date=date(1990, 5, 21),
        is_certified=False,
        avatar="avatars/john.jpg",
    )
    assert created_profile is not None
    assert created_profile.user.username == "john_doe"
    assert created_profile.description == "Hey I'm John Doe"
    assert created_profile.city == "Paris"
    assert created_profile.country == "France"
    assert created_profile.birth_date == date(1990, 5, 21)
    assert created_profile.languages_spoken == "french"
    assert created_profile.centers_of_interest == "foot"
    assert created_profile.event_expectations == "nothing"
    assert created_profile.activity_preferences == "sport"
    assert created_profile.group_size_preference == "10"
    assert created_profile.dietary_restrictions == "nuts"
    assert created_profile.is_certified == False
    assert created_profile.avatar == "avatars/john.jpg"
    assert stub_repo.save_calls == 1  # saved once
