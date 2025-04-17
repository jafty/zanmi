# infrastructure/stubs.py (or just in tests if it's only used for that)
from domain.repositories.payment_gateway import PaymentGateway


class StubPaymentGateway(PaymentGateway):
    def __init__(self, should_fail_creation=False, should_fail_capture=False, should_fail_cancel=False):
        self.should_fail_creation = should_fail_creation
        self.should_fail_capture = should_fail_capture
        self.should_fail_cancel = should_fail_cancel
        self.created_payments = []
        self.captured_payments = []
        self.cancelled_payments = []

    def create_payment(self, user, event, amount_in_cents):
        if self.should_fail_creation:
            return None
        payment_id = f"stub_pi_{len(self.created_payments) + 1}"
        self.created_payments.append({
            "payment_id": payment_id,
            "user": user,
            "event": event,
            "amount": amount_in_cents
        })
        return payment_id

    def capture(self, payment_id):
        if self.should_fail_capture:
            raise Exception("Stub capture failed")
        self.captured_payments.append(payment_id)

    def cancel(self, payment_id):
        if self.should_fail_cancel:
            raise Exception("Stub cancel failed")
        self.cancelled_payments.append(payment_id)
