from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.models.service import ServiceBooking, AppointmentStatusHistory
from app.models.user import Technician
from app.models.communication import Notification, Announcement
from app.forms import ServiceStatusForm
from app.utils.decorators import technician_required
from app.utils.helpers import get_status_color
from datetime import datetime, date
from sqlalchemy import func

technician_bp = Blueprint('technician', __name__)


def _get_tech():
    """Return the Technician profile for the current user."""
    return Technician.query.filter_by(user_id=current_user.id).first()


@technician_bp.route('/dashboard')
@login_required
@technician_required
def dashboard():
    tech = _get_tech()
    tech_id = tech.id if tech else 0

    pending_appointments = ServiceBooking.query.filter_by(technician_id=tech_id).filter(
        ServiceBooking.status.in_(['PENDING', 'CONFIRMED', 'ASSIGNED'])).count() if tech else 0
    active_services = ServiceBooking.query.filter_by(technician_id=tech_id).filter(
        ServiceBooking.status == 'PROCESSING').count() if tech else 0
    completed_services = ServiceBooking.query.filter_by(technician_id=tech_id).filter(
        ServiceBooking.status == 'COMPLETED').count() if tech else 0
    today_appointments = ServiceBooking.query.filter_by(technician_id=tech_id).filter(
        ServiceBooking.booking_date == date.today()).count() if tech else 0

    recent_appointments = ServiceBooking.query.filter_by(technician_id=tech_id).order_by(
        ServiceBooking.created_at.desc()).limit(10).all() if tech else []
    announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.created_at.desc()).limit(5).all()

    return render_template('technician/dashboard.html',
                          pending_appointments=pending_appointments,
                          active_services=active_services,
                          completed_services=completed_services,
                          today_appointments=today_appointments,
                          recent_appointments=recent_appointments,
                          announcements=announcements,
                          tech=tech)


@technician_bp.route('/appointments')
@login_required
@technician_required
def appointments():
    tech = _get_tech()
    if not tech:
        flash('Technician profile not found.', 'warning')
        return redirect(url_for('technician.dashboard'))

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = ServiceBooking.query.filter_by(technician_id=tech.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(ServiceBooking.created_at.desc()).paginate(page=page, per_page=10)
    
    # Get status counts for summary cards
    status_counts = {}
    results = ServiceBooking.query.filter_by(technician_id=tech.id).with_entities(
        ServiceBooking.status, func.count(ServiceBooking.id)).group_by(ServiceBooking.status).all()
    for status_name, count in results:
        status_counts[status_name] = count

    return render_template('technician/appointments.html',
                          appointments=appointments, current_status=status, status_counts=status_counts)


@technician_bp.route('/appointments/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@technician_required
def appointment_detail(appointment_id):
    tech = _get_tech()
    if not tech:
        flash('Technician profile not found.', 'warning')
        return redirect(url_for('technician.dashboard'))

    booking = ServiceBooking.query.get_or_404(appointment_id)
    # Technicians can only view their own assigned appointments
    if booking.technician_id != tech.id and not current_user.is_admin:
        from flask import abort
        abort(403)

    form = ServiceStatusForm()
    # Technicians cannot reassign technicians, so give the field a valid (unused) choice set
    form.technician_id.choices = [(0, 'None')]
    if form.validate_on_submit():
        old_status = booking.status
        booking.status = form.status.data
        history = AppointmentStatusHistory(
            booking_id=booking.id, old_status=old_status,
            new_status=form.status.data, note=form.note.data,
            updated_by=current_user.id
        )
        db.session.add(history)
        notif = Notification(
            user_id=booking.user_id, title='Appointment Status Updated',
            message=f'Your booking {booking.booking_number} status changed to {form.status.data}.',
            notification_type='info', link=f'/customer/appointments/{booking.id}'
        )
        db.session.add(notif)
        db.session.commit()
        flash('Appointment status updated.', 'success')
        return redirect(url_for('technician.appointment_detail', appointment_id=appointment_id))

    form.status.data = booking.status
    form.technician_id.data = booking.technician_id or 0
    status_history = AppointmentStatusHistory.query.filter_by(
        booking_id=booking.id).order_by(AppointmentStatusHistory.created_at).all()
    return render_template('technician/appointment_detail.html', booking=booking, form=form,
                          status_history=status_history, status_color=get_status_color)


@technician_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@technician_required
def profile():
    tech = _get_tech()
    if request.method == 'POST':
        tech.skills = request.form.get('skills', tech.skills)
        tech.bio = request.form.get('bio', tech.bio)
        tech.experience_years = request.form.get('experience_years', tech.experience_years, type=int)
        tech.hourly_rate = request.form.get('hourly_rate', tech.hourly_rate, type=float)
        is_available = request.form.get('is_available')
        tech.is_available = True if is_available == 'on' else False
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('technician.profile'))
    return render_template('technician/profile.html', tech=tech)
