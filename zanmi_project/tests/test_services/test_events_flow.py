from services.events_services import create_event, get_event_detail
from domain.user import User
from domain.event import Event
from datetime import datetime


class StubEventRepository:
    def __init__(self):
        self.saved_event = None

    def save_event(self, event):
        self.saved_event = event

    def get_event_by_id(self, event_id):
        # You can make this more sophisticated if needed
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


def test_get_event_detail_returns_event():
    repo = StubEventRepository()
    expected_event = Event(start_datetime=..., organizer=..., price=...)
    repo.save_event(expected_event)
    result = get_event_detail(event_id=123, repo=repo)  # id is ignored
    assert result == expected_event

