# events_app/repositories.py
from domain.event import Event
from django.contrib.auth import get_user_model
from domain.participation import Participation
from domain.user import User
from domain.repositories.event_repository import EventRepository
from domain.repositories.participation_repository import ParticipationRepository
from .models import EventDB, ParticipationDB

UserDB = get_user_model()

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


class DjangoParticipationRepository(ParticipationRepository):
    def save_participation(self, participation: Participation):
        db_user = UserDB.objects.get(username=participation.user.username)
        db_event = EventDB.objects.get(
            start_datetime=participation.event.start_datetime,
            organizer__username=participation.event.organizer.username
        )
        ParticipationDB.objects.create(
            user=db_user,
            event=db_event,
            status=participation.status,
            payment_id=participation.payment_id,
            message=participation.message
        )

    def get_existing_participation(self, user_id: int, event_id: int):
        return ParticipationDB.objects.filter(user_id=user_id, event_id=event_id).first()