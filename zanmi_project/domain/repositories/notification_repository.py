from abc import ABC, abstractmethod
from domain.notification import Notification

class NotificationRepository(ABC):
    
    @abstractmethod
    def save_notification(self, notification: Notification) -> None:
        pass

    @abstractmethod
    def get_notifications_for_user(self, user_id: int) -> list[Notification]:
        pass