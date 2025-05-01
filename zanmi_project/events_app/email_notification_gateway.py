from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailNotificationGateway:
    def send(self, notification) -> bool:
        recipient = notification.recipient
        message_body = notification.message
        if not recipient or not getattr(recipient, 'email', None):
            logger.warning("Email sending failed: Recipient email missing.")
            return False
        recipient_email = recipient.email
        email_subject = 'New Notification from ' + notification.sender.username + ' about ' + notification.event.title 
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