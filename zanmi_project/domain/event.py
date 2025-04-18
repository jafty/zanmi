# domain/event.py
from datetime import datetime
from domain.user import User
from services.queries import get_price_in_cents

class Event:
    def __init__(
        self,
        title: str,
        location: str,
        start_datetime: datetime,
        organizer: User,
        price: float = 0,
        description: str = "",
        time: str = "",
        activity_type: str = "",
        image_url: str = ""
    ):
        self.title = title
        self.location = location
        self.start_datetime = start_datetime
        self.organizer = organizer
        self.price = price
        self.description = description
        self.time = time
        self.activity_type = activity_type
        self.image_url = image_url

    def is_past(self, now: datetime) -> bool:
        return self.start_datetime.date() < now.date()

    def is_manageable_by(self, user: User) -> bool:
        return self.organizer.username == user.username

    def checkout_user(self, user: User, payment_gateway, message=""):
        price_cents = get_price_in_cents(self.price)
        payment_id = payment_gateway.create_payment(user, self, price_cents, message)
        if payment_id:
            return payment_id
        return False

    def add_participation(self, user: User, message=""):
        price_cents = get_price_in_cents(self.price)
        return Participation(
            user=user,
            event=self,
            status="PENDING",
            message=message
        )


class Participation:
    
    def __init__(self, user: User, event: Event, status="PENDING", payment_id=None, message=""):
        self.user = user
        self.event = event
        self.status = status
        self.payment_id = payment_id
        self.message = message
    
    def is_pending(self):
        return self.status == "PENDING"

    def is_accepted(self):
        return self.status == "ACCEPTED"
    
    def is_rejected(self):
        return self.status == "REJECTED"
    
    def reject(self):
        self.status = "REJECTED"

    def accept(self):
        self.status = "ACCEPTED"