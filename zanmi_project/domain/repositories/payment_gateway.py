class PaymentGateway:
    def create_payment(self, user, event, amount_in_cents, message):
        raise NotImplementedError

    def capture(self, payment_id):
        raise NotImplementedError

    def cancel(self, payment_id):
        raise NotImplementedError
