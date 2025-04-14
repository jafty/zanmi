from datetime import datetime
from domain.event import Event
from domain.user import User
from services.events_queries import get_price_in_cents, can_manage


def test_can_manage_if_user_is_organizer():
    user = User(username="Organizer")
    event = Event(start_datetime=datetime(2025, 4, 20), organizer=user)
    assert can_manage(user, event) is True


def test_cannot_manage__if_user_is_not_organizer():
    organizer = User(username="Organizer")
    stranger = User(username="Alice")
    event = Event(start_datetime=datetime(2025, 4, 20), organizer=organizer)
    assert can_manage(stranger, event) is False


def test_get_price_in_cents():
    assert get_price_in_cents(12.50) == 1250
    assert get_price_in_cents(0) == 0