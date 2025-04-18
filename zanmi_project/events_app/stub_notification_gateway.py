class StubNotificationGateway:
    
    def send(self, notification):
        print(f"[NOTIFY] To {notification.recipient.username}: {notification.message}")
        return True