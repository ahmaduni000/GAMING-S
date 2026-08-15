from datetime import datetime
from app import db


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    image = db.Column(db.String(255), default='default_service.png')
    fee = db.Column(db.Float, default=0.0)
    estimated_duration = db.Column(db.String(50))  # e.g. "2-3 hours"
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('ServiceBooking', backref='service', lazy='dynamic')

    def __repr__(self):
        return f'<Service {self.name}>'


class ServiceBooking(db.Model):
    __tablename__ = 'service_bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('technicians.id'))
    status = db.Column(db.String(30), default='PENDING')
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.String(20), nullable=False)
    service_location = db.Column(db.String(200))
    problem_description = db.Column(db.Text)
    service_fee = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.String(30), default='PENDING')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    status_history = db.relationship('AppointmentStatusHistory', backref='booking', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else 'Unknown'

    @property
    def technician_name(self):
        if self.technician:
            return self.technician.user.full_name
        return 'Not Assigned'

    def generate_booking_number(self):
        import random
        import string
        prefix = 'APT'
        nums = ''.join(random.choices(string.digits, k=8))
        return f'{prefix}-{nums}'

    def __repr__(self):
        return f'<ServiceBooking {self.booking_number}>'


class AppointmentStatusHistory(db.Model):
    __tablename__ = 'appointment_status_history'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('service_bookings.id'), nullable=False)
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updater = db.relationship('User', backref='appointment_status_updates')

    def __repr__(self):
        return f'<AppointmentStatusHistory {self.new_status}>'
