from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.models.order import Order, OrderItem, Payment, PaymentProof
from app.models.service import ServiceBooking
from app.models.cart import Wishlist, WishlistItem
from app.models.review import Review
from app.models.communication import Notification
from app.models.product import Product
from app.forms import ReviewForm, ProfileForm, ChangePasswordForm
from app.utils.decorators import customer_required
from app.utils.file_upload import save_upload
from app.utils.helpers import get_status_color
from datetime import datetime

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    pending_orders = Order.query.filter_by(user_id=current_user.id).filter(
        Order.status.in_(['PENDING', 'CONFIRMED', 'PROCESSING'])).count()
    completed_orders = Order.query.filter_by(user_id=current_user.id, status='DELIVERED').count()
    total_appointments = ServiceBooking.query.filter_by(user_id=current_user.id).count()
    pending_appointments = ServiceBooking.query.filter_by(user_id=current_user.id).filter(
        ServiceBooking.status.in_(['PENDING', 'CONFIRMED'])).count()
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()

    return render_template('customer/dashboard.html',
                         total_orders=total_orders, pending_orders=pending_orders,
                         completed_orders=completed_orders,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         recent_orders=recent_orders, notifications=notifications)


@customer_bp.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Order.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('customer/orders.html', orders=orders, current_status=status)


@customer_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.orders'))
    status_history = order.status_history.order_by(OrderStatusHistory=order.status_history.order().first() if False else None)
    from app.models.order import OrderStatusHistory
    status_history = OrderStatusHistory.query.filter_by(order_id=order.id).order_by(OrderStatusHistory.created_at).all()
    return render_template('customer/order_detail.html', order=order,
                         status_history=status_history,
                         status_color=get_status_color)


@customer_bp.route('/orders/<int:order_id>/upload-payment', methods=['POST'])
@login_required
def upload_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.orders'))
    screenshot = request.files.get('screenshot')
    if not screenshot or screenshot.filename == '':
        flash('Please upload a payment screenshot.', 'danger')
        return redirect(url_for('customer.order_detail', order_id=order_id))
    image_path = save_upload(screenshot, 'payments')
    payment = Payment(
        order_id=order.id,
        amount=order.total,
        method='online',
        status='WAITING_FOR_VERIFICATION'
    )
    db.session.add(payment)
    db.session.flush()
    proof = PaymentProof(
        payment_id=payment.id,
        screenshot_url=image_path,
        sender_account=request.form.get('sender_account', ''),
        sender_name=request.form.get('sender_name', ''),
        amount_sent=float(request.form.get('amount_sent', order.total)),
        transaction_reference=request.form.get('transaction_ref', ''),
        status='WAITING_FOR_VERIFICATION'
    )
    db.session.add(proof)
    order.payment_status = 'WAITING_FOR_VERIFICATION'
    db.session.commit()
    flash('Payment proof uploaded. Waiting for verification.', 'success')
    return redirect(url_for('customer.order_detail', order_id=order_id))


@customer_bp.route('/appointments')
@login_required
def appointments():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = ServiceBooking.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(ServiceBooking.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('customer/appointments.html', appointments=appointments, current_status=status)


@customer_bp.route('/appointments/<int:appointment_id>')
@login_required
def appointment_detail(appointment_id):
    from app.models.service import AppointmentStatusHistory
    booking = ServiceBooking.query.get_or_404(appointment_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.appointments'))
    status_history = AppointmentStatusHistory.query.filter_by(booking_id=booking.id).order_by(AppointmentStatusHistory.created_at).all()
    return render_template('customer/appointment_detail.html', booking=booking,
                         status_history=status_history,
                         status_color=get_status_color)


@customer_bp.route('/wishlist')
@login_required
def wishlist():
    wl = Wishlist.query.filter_by(user_id=current_user.id).first()
    items = []
    if wl:
        items = WishlistItem.query.filter_by(wishlist_id=wl.id).all()
    return render_template('customer/wishlist.html', items=items)


@customer_bp.route('/wishlist/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_wishlist(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    wl = Wishlist.query.filter_by(user_id=current_user.id).first()
    if not wl or item.wishlist_id != wl.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.wishlist'))
    db.session.delete(item)
    db.session.commit()
    flash('Removed from wishlist.', 'info')
    return redirect(url_for('customer.wishlist'))


@customer_bp.route('/reviews')
@login_required
def reviews():
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('customer/reviews.html', reviews=reviews)


@customer_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('customer/notifications.html', notifications=notifications)


@customer_bp.route('/notifications/read/<int:notif_id>')
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('customer.notifications'))
    notif.is_read = True
    db.session.commit()
    if notif.link:
        return redirect(notif.link)
    return redirect(url_for('customer.notifications'))


@customer_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    return redirect(url_for('customer.notifications'))
