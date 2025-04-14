from abc import ABC, abstractmethod

class EventRepository(ABC):
    @abstractmethod
    def get_event_by_id(self, event_id: int):
        pass