import pytest
from datetime import datetime
from domain.user import User
from domain.event import Event
from domain.participation import Participation
from services.events_services import *
from services.events_queries import *
from unittest.mock import Mock
import sys
import os


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


def test_user_joins_event_and_gets_pending_participation(participant, event):
    existing_participations = []
    mock_gateway = Mock()
    mock_gateway.create_payment.return_value = "fake_payment_id"
    participation = join_event(
        participant, 
        event, 
        existing_participations, 
        payment_gateway=mock_gateway, 
        message="Looking forward to it!"
    )
    assert isinstance(participation, Participation)
    assert participation.user == participant
    assert participation.event == event
    assert participation.status == "PENDING"
    assert participation.payment_id == "fake_payment_id"
    assert participation.message == "Looking forward to it!"
    mock_gateway.create_payment.assert_called_once_with(participant, event, 2500)  # Assuming price = 25.00


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
    updated_participation = reject_participation(organizer=organizer, participation=participation)
    assert updated_participation.status == "REJECTED"


def test_user_status_is_organizer(organizer, event):
    status = get_user_event_status(organizer, event, participation=None)
    assert status == "organizer"


def test_user_status_is_accepted(participant: User, event: Event):
    participation = Participation(user=participant, event=event, status="ACCEPTED")
    status = get_user_event_status(participant, event, participation)
    assert status == "ACCEPTED"


def test_user_status_is_pending(participant, event):
    participation = Participation(user=participant, event=event, status="PENDING")
    status = get_user_event_status(participant, event, participation)
    assert status == "PENDING"


def test_user_status_is_rejected(participant, event):
    participation = Participation(user=participant, event=event, status="REJECTED")
    status = get_user_event_status(participant, event, participation)
    assert status == "REJECTED"


def test_user_status_is_none(participant, event):
    # Not the organizer, and has no participation
    status = get_user_event_status(participant, event, participation=None)
    assert status == "none"
