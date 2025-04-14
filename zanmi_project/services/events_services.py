# services/events_services.py

from domain.participation import Participation
from domain.user import User
from domain.event import Event
from domain.repositories.event_repository import EventRepository
from services.events_queries import *


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


def join_event(user: User, event: Event, existing_participations, payment_gateway, message=""):
    price_cents = get_price_in_cents(event.price)
    payment_id = payment_gateway.create_payment(user, event, price_cents)
    return Participation(
        user=user,
        event=event,
        status="PENDING",
        payment_id=payment_id,
        message=message
    )


def accept_participation(organizer: User, participation: Participation, payment_gateway):
    if participation.payment_id and payment_gateway:
        payment_gateway.capture(participation.payment_id)
    return Participation(participation.user, participation.event, status="ACCEPTED")


def reject_participation(organizer: User, participation: Participation):
    return Participation(participation.user, participation.event, status="REJECTED")

