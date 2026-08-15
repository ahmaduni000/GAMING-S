from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user
from app import db
from app.models.order import Order, OrderStatusHistory
from app.models.service import ServiceBooking, AppointmentStatusHistory
from app.models.user import Technician, User
from app.models.communication import Notification, Announcement
from app.forms import OrderStatusForm, ServiceStatusForm, LoginForm
from app.utils.decorators import staff_required, log_activity
from app.utils.helpers import get_status_color
from datetime import datetime
from sqlalchemy import func

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/login', methods=['GET', 'POST'])
def staff_login():
    """Dedicated login for staff, admin, and technicians (separate from customer login)."""
    if current_user.is_authenticated:
        if current_user.is_customer:
            flash('This portal is for staff, admin, and technicians only.', 'warning')
            return redirect(url_for('customer.dashboard'))
        from app.routes.auth import get_dashboard_url
        return redirect(get_dashboard_url())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('staff.staff_login'))
            if not (user.is_admin or user.is_staff or user.is_technician_role):
                flash('This login is for staff, admin, and technicians only. '
                      'Customers should use the main login page.', 'warning')
                return redirect(url_for('staff.staff_login'))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login', f'Staff member {user.username} logged in via staff portal')
            flash(f'Welcome back, {user.first_name}!', 'success')
            from app.routes.auth import get_dashboard_url
            return redirect(get_dashboard_url())
        flash('Invalid email or password.', 'danger')
    return render_template('staff/login.html', form=form)


@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    if current_user.is_technician_role:
        tech = Technician.query.filter_by(user_id=current_user.id).first()
        assigned_orders = Order.query.filter(Order.status.in_(['PROCESSING', 'PACKED', 'SHIPPED'])).count()
        pending_appointments = ServiceBooking.query.filter_by(technician_id=tech.id if tech else 0).filter(
            ServiceBooking.status.in_(['PENDING', 'CONFIRMED', 'ASSIGNED'])).count() if tech else 0
        active_services = ServiceBooking.query.filter_by(technician_id=tech.id if tech else 0).filter(
            ServiceBooking.status == 'PROCESSING').count() if tech else 0
        from datetime import date
        today_appointments = ServiceBooking.query.filter_by(technician_id=tech.id if tech else 0).filter(
            ServiceBooking.booking_date==date.today()).count() if tech else 0
    else:
        assigned_orders = Order.query.filter(Order.status.in_(['CONFIRMED', 'PROCESSING', 'PACKED'])).count()
        pending_appointments = ServiceBooking.query.filter(
            ServiceBooking.status.in_(['PENDING', 'CONFIRMED'])).count()
        active_services = ServiceBooking.query.filter_by(status='PROCESSING').count()
        from datetime import date
        today_appointments = ServiceBooking.query.filter(
            ServiceBooking.booking_date==date.today()).count()

    pending_orders = Order.query.filter_by(status='PENDING').count()
    completed_orders = Order.query.filter_by(status='DELIVERED').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()

    return render_template('staff/dashboard.html',
                         assigned_orders=assigned_orders, pending_orders=pending_orders,
                         completed_orders=completed_orders, pending_appointments=pending_appointments,
                         active_services=active_services, today_appointments=today_appointments,
                         recent_orders=recent_orders, announcements=announcements)


@staff_bp.route('/orders')
@login_required
@staff_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('staff/orders.html', orders=orders, current_status=status)


@staff_bp.route('/orders/<int:order_id>')
@login_required
@staff_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm()
    if form.validate_on_submit():
        old_status = order.status
        order.status = form.status.data
        history = OrderStatusHistory(
            order_id=order.id, old_status=old_status,
            new_status=form.status.data, note=form.note.data,
            updated_by=current_user.id
        )
        db.session.add(history)
        notif = Notification(
            user_id=order.user_id, title='Order Status Updated',
            message=f'Your order {order.order_number} status changed to {form.status.data}.',
            notification_type='info', link=f'/customer/orders/{order.id}'
        )
        db.session.add(notif)
        db.session.commit()
        flash('Order status updated.', 'success')
        return redirect(url_for('staff.order_detail', order_id=order_id))
    form.status.data = order.status
    status_history = OrderStatusHistory.query.filter_by(order_id=order.id).order_by(OrderStatusHistory.created_at).all()
    return render_template('staff/order_detail.html', order=order, form=form,
                         status_history=status_history, status_color=get_status_color)


@staff_bp.route('/appointments')
@login_required
@staff_required
def appointments():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = ServiceBooking.query
    if current_user.is_technician_role:
        tech = Technician.query.filter_by(user_id=current_user.id).first()
        if tech:
            query = query.filter_by(technician_id=tech.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(ServiceBooking.created_at.desc()).paginate(page=page, per_page=10)
    
    # Get status counts for summary cards
    status_counts = {}
    all_bookings = ServiceBooking.query
    if current_user.is_technician_role:
        tech = Technician.query.filter_by(user_id=current_user.id).first()
        if tech:
            all_bookings = all_bookings.filter_by(technician_id=tech.id)
    results = all_bookings.with_entities(ServiceBooking.status, func.count(ServiceBooking.id)).group_by(ServiceBooking.status).all()
    for status_name, count in results:
        status_counts[status_name] = count
    
    return render_template('staff/appointments.html', appointments=appointments, current_status=status, status_counts=status_counts)


@staff_bp.route('/appointments/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@staff_required
def appointment_detail(appointment_id):
    booking = ServiceBooking.query.get_or_404(appointment_id)
    form = ServiceStatusForm()
    from app.models.user import Technician
    technicians = Technician.query.filter_by(is_available=True).all()
    form.technician_id.choices = [(0, 'None')] + [(t.id, t.user.full_name) for t in technicians]

    if form.validate_on_submit():
        old_status = booking.status
        booking.status = form.status.data
        if form.technician_id.data and form.technician_id.data != 0:
            booking.technician_id = form.technician_id.data
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
        return redirect(url_for('staff.appointment_detail', appointment_id=appointment_id))

    form.status.data = booking.status
    form.technician_id.data = booking.technician_id or 0
    status_history = AppointmentStatusHistory.query.filter_by(booking_id=booking.id).order_by(AppointmentStatusHistory.created_at).all()
    return render_template('staff/appointment_detail.html', booking=booking, form=form,
                         status_history=status_history, status_color=get_status_color)
