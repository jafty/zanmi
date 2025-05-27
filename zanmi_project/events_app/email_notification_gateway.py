from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
UserModel = get_user_model()

class EmailNotificationGateway:

    def send(self, notification) -> bool:
        domain_user = notification.recipient
        try:
            django_user = UserModel.objects.get(username=domain_user.username)
        except UserModel.DoesNotExist:
            logger.error(f"Impossible de trouver l'utilisateur Django '{domain_user.username}'")
            return False
        message_body = notification.message
        recipient_email = django_user.email
        if notification.sender is None:
            sender_username = "Zanmi Team"
            sender_email = settings.DEFAULT_FROM_EMAIL
        else:
            sender_username = notification.sender.username

        email_subject = 'New Notification from ' + sender_username + ' about ' + notification.event.title 
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            print(f"Sending email to {recipient_email}: {message_body}")
            email = EmailMessage(
                subject=email_subject,
                body=message_body,
                from_email=from_email,
                to=[recipient_email],
            )
            email.send()
            print(f"Email sent to {recipient_email}: {message_body}")
            logger.info(f"Email sent to {recipient_email}: {message_body}")
            # Log the email sending
            return True
        except Exception as e:
            logger.error(f"Email sending failed to {recipient_email}: {e}")
            return False

    def send_many(self, notifications):
        for notification in notifications:
            self.send(notification)
