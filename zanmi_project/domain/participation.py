from domain.user import User
from domain.event import Event

class Participation:
    
    def __init__(self, user: User, event: Event, status="PENDING", payment_id=None, message=""):
        self.user = user
        self.event = event
        self.status = status
        self.payment_id = payment_id
        self.message = message
