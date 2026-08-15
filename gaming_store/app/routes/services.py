from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.models.service import Service, ServiceBooking, AppointmentStatusHistory
from app.models.user import Technician
from app.models.communication import Notification
from app.forms import ServiceBookingForm
from app.utils.helpers import generate_booking_number
from datetime import datetime

services_bp = Blueprint('services', __name__)


@services_bp.route('/')
def listing():
    services = Service.query.filter_by(is_active=True).order_by(Service.sort_order).all()
    return render_template('main/services.html', services=services)


@services_bp.route('/<slug>')
def detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    technicians = Technician.query.filter_by(is_available=True).all()
    return render_template('main/service_detail.html', service=service, technicians=technicians)


@services_bp.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceBookingForm()
    form.service_id.data = service.id
    form.service_id.choices = [(service.id, service.name)]

    technicians = Technician.query.filter_by(is_available=True).all()
    form.technician_id.choices = [(0, 'Auto-assign')] + [(t.id, t.user.full_name) for t in technicians]

    if form.validate_on_submit():
        technician_id = form.technician_id.data if form.technician_id.data != 0 else None
        booking = ServiceBooking(
            booking_number=generate_booking_number(),
            service_id=service.id,
            user_id=current_user.id,
            technician_id=technician_id,
            booking_date=form.booking_date.data,
            booking_time=form.booking_time.data,
            service_location=form.service_location.data,
            problem_description=form.problem_description.data,
            service_fee=service.fee,
            payment_method=form.payment_method.data,
            payment_status='PENDING'
        )
        db.session.add(booking)
        db.session.flush()

        status_hist = AppointmentStatusHistory(
            booking_id=booking.id,
            new_status='PENDING',
            note='Booking created',
            updated_by=current_user.id
        )
        db.session.add(status_hist)

        notif = Notification(
            user_id=current_user.id,
            title='Service Booked',
            message=f'Your booking {booking.booking_number} for {service.name} has been submitted.',
            notification_type='success',
            link=f'/customer/appointments/{booking.id}'
        )
        db.session.add(notif)
        service.total_bookings += 1
        db.session.commit()

        flash(f'Booking {booking.booking_number} submitted successfully!', 'success')
        return redirect(url_for('customer.appointment_detail', appointment_id=booking.id))

    return render_template('main/book_service.html', service=service, form=form)
