from datetime import datetime
from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), default='PENDING', nullable=False)
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    delivery_fee = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20), nullable=False)  # cod or online
    payment_status = db.Column(db.String(30), default='PENDING')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    billing = db.relationship('BillingDetail', backref='order', uselist=False, lazy=True)
    payments = db.relationship('Payment', backref='order', lazy='dynamic')
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def item_count(self):
        return self.items.count()

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else 'Unknown'

    @property
    def shipping_address(self):
        if self.billing:
            return f'{self.billing.address}, {self.billing.city}'
        return 'No address provided'

    def generate_order_number(self):
        import random
        import string
        prefix = 'GS'
        nums = ''.join(random.choices(string.digits, k=8))
        return f'{prefix}-{nums}'

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    subtotal = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OrderItem {self.product_name}>'


class BillingDetail(db.Model):
    __tablename__ = 'billing_details'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BillingDetail {self.full_name}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='PENDING')
    transaction_id = db.Column(db.String(100))
    notes = db.Column(db.Text)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    verifier = db.relationship('User', backref='verified_payments')
    proof = db.relationship('PaymentProof', backref='payment', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Payment {self.id} - {self.status}>'


class PaymentProof(db.Model):
    __tablename__ = 'payment_proofs'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False, unique=True)
    screenshot_url = db.Column(db.String(500), nullable=False)
    sender_account = db.Column(db.String(100))
    sender_name = db.Column(db.String(100))
    amount_sent = db.Column(db.Float)
    transaction_reference = db.Column(db.String(100))
    rejection_reason = db.Column(db.Text)
    verification_note = db.Column(db.Text)
    status = db.Column(db.String(30), default='WAITING_FOR_VERIFICATION')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PaymentProof {self.id} - {self.status}>'


class OrderStatusHistory(db.Model):
    __tablename__ = 'order_status_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updater = db.relationship('User', backref='order_status_updates')

    def __repr__(self):
        return f'<OrderStatusHistory {self.new_status}>'
