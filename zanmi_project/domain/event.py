# domain/event.py
from datetime import datetime
from domain.user import User

class Event:
    def __init__(
        self,
        start_datetime: datetime,
        organizer: User,
        price: float = 0,
        description: str = "",
        time: str = "",
        activity_type: str = "",
        image_url: str = ""
    ):
        self.start_datetime = start_datetime
        self.organizer = organizer
        self.price = price
        self.description = description
        self.time = time
        self.activity_type = activity_type
        self.image_url = image_url

    def is_past(self, now: datetime) -> bool:
        return self.start_datetime.date() < now.date()
