import sys
import os
import pytest
from datetime import datetime
from domain.event import Event
from domain.user import User


# DATES
# -----
@pytest.fixture
def current_date():
    current_date= datetime(2025, 4, 11)
    return current_date 

@pytest.fixture
def event():
    user = User("Alice")
    event_date = datetime(2025, 4, 11)
    organizer = User("Host")
    event = Event(event_date, user, organizer)
    return event


def test_event_is_not_past_if_today(event, current_date):
    assert event.is_past(current_date) is False


def test_event_is_not_past_if_in_future(event):
    a_date_before = datetime(2025, 4, 10)
    assert event.is_past(a_date_before) is False


def test_event_is_past_if_in_past(event):
    a_date_after = datetime(2025, 4, 12)
    assert event.is_past(a_date_after) is True



