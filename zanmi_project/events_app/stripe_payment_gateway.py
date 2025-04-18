# infrastructure/stripe_payment_gateway.py
from domain.repositories.payment_gateway import PaymentGateway  
from django.conf import settings    
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY  # ← make sure this is set

class StripePaymentGateway(PaymentGateway):
    def create_payment(self, user, event, amount_in_cents, message=""):
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": event.title},
                    "unit_amount": int(amount_in_cents),  # make sure this is an integer
                },
                "quantity": 1,
            }],
            mode="payment",
            payment_intent_data={"capture_method": "manual"},
            metadata={
                "username": user.username,
                "event_title": event.title,
                "message": message,
            },
            success_url=f"{settings.BASE_URL}/stripe_success/",
            cancel_url=f"{settings.BASE_URL}/stripe_cancel/",
        )
        return session.url  # ✅ directly return checkout URL

    def capture(self, payment_id):
        return stripe.PaymentIntent.capture(payment_id)

    def cancel(self, payment_id):
        return stripe.PaymentIntent.cancel(payment_id)
