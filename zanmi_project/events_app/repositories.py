# events_app/repositories.py
from domain.event import Event
from domain.user import User
from domain.repositories.event_repository import EventRepository
from .models import EventDB

class DjangoEventRepository(EventRepository):
    def get_event_by_id(self, event_id: int) -> Event:
        model = EventDB.objects.select_related("organizer").get(id=event_id)
        organizer = User(username=model.organizer.username)
        return Event(
            start_datetime=model.start_datetime,
            organizer=organizer,
            price=float(model.price),
            description=model.description or "",
            time=model.time or "",
            activity_type=model.activity_type or "",
            image_url=model.image.url if model.image else ""
        )
