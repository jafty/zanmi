from domain.user import User
from domain.event import Event
from domain.participation import Participation


def get_price_in_cents(euro_price: float):
    return euro_price*100


def get_user_event_status(user: User, event: Event, participation: Participation):
    if user == event.organizer:
        return "organizer"
    elif participation:
        return participation.status
    return "none"


def can_manage(user: User, event: Event) -> bool:
    return event.organizer == user




