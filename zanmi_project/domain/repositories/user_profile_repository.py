# domain/repositories/user_profile_repository.py
from abc import ABC, abstractmethod
from domain.user_profile import UserProfile

class UserProfileRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> UserProfile:
        pass

    @abstractmethod
    def save_user_profile(self, profile: UserProfile) -> None:
        pass
