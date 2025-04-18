class Notification:
    def __init__(self, recipient, sender, message, event=None):
        self.recipient = recipient
        self.sender = sender
        self.message = message
        self.event = event
