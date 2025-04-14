# domain/repositories/participation_repository.py
from abc import ABC, abstractmethod

class ParticipationRepository(ABC):
    @abstractmethod
    def save_participation(self, participation): pass

    @abstractmethod
    def get_existing_participation(self, user, event): pass
