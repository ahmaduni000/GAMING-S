from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.user import User, Role, Technician, ActivityLog
from app.models.product import Product, Category, ProductImage, ProductSpecification, Inventory
from app.models.order import Order, OrderItem, Payment, PaymentProof, OrderStatusHistory, BillingDetail
from app.models.service import Service, ServiceBooking, AppointmentStatusHistory
from app.models.review import Review
from app.models.communication import ContactMessage, Announcement, Notification, Banner
from app.models.settings import SiteSettings, PaymentSettings
from app.forms import (CategoryForm, ProductForm, ServiceForm, BannerForm,
                       AnnouncementForm, PaymentSettingsForm, UserForm, TechnicianForm,
                       PaymentVerificationForm, OrderStatusForm, ServiceStatusForm)
from app.utils.decorators import admin_required
from app.utils.file_upload import save_upload, delete_upload
from app.utils.helpers import get_status_color, slugify
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_revenue = db.session.query(func.sum(Order.total)).filter(Order.status=='DELIVERED').scalar() or 0
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='PENDING').count()
    completed_orders = Order.query.filter_by(status='DELIVERED').count()
    total_customers = User.query.join(User.roles).filter(Role.name=='customer').count()
    total_staff = User.query.join(User.roles).filter(Role.name=='staff').count()
    total_technicians = Technician.query.count()
    total_products = Product.query.count()
    low_stock = Product.query.filter(Product.stock_quantity <= Product.low_stock_threshold, Product.is_active==True).count()
    total_services = Service.query.count()
    total_appointments = ServiceBooking.query.count()
    pending_payments = Payment.query.filter_by(status='WAITING_FOR_VERIFICATION').count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.filter_by(is_read=False).order_by(ContactMessage.created_at.desc()).limit(5).all()

    monthly_revenue = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        rev = db.session.query(func.sum(Order.total)).filter(
            Order.created_at >= month_start, Order.created_at < month_end,
            Order.status == 'DELIVERED'
        ).scalar() or 0
        monthly_revenue.append(float(rev))
        monthly_labels.append(month_start.strftime('%b %Y'))

    return render_template('admin/dashboard.html',
                         total_revenue=total_revenue, total_orders=total_orders,
                         pending_orders=pending_orders, completed_orders=completed_orders,
                         total_customers=total_customers, total_staff=total_staff,
                         total_technicians=total_technicians, total_products=total_products,
                         low_stock=low_stock, total_services=total_services,
                         total_appointments=total_appointments, pending_payments=pending_payments,
                         recent_orders=recent_orders, recent_messages=recent_messages,
                         monthly_revenue=monthly_revenue, monthly_labels=monthly_labels)


# --- CUSTOMERS ---
@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    query = User.query.join(User.roles).filter(Role.name=='customer')
    if search:
        query = query.filter(User.username.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/customers.html', users=users, search=search)


@admin_bp.route('/customers/<int:user_id>')
@login_required
@admin_required
def customer_detail(user_id):
    user = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return render_template('admin/customer_detail.html', user=user, orders=orders)


@admin_bp.route('/customers/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_customer(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'Customer {user.username} {"activated" if user.is_active else "deactivated"}.', 'info')
    return redirect(url_for('admin.customers'))


@admin_bp.route('/customers/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_customer(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Customer deleted.', 'success')
    return redirect(url_for('admin.customers'))


# --- PRODUCTS ---
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    cat = request.args.get('category', type=int)
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if cat:
        query = query.filter_by(category_id=cat)
    products = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=15)
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories, search=search)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def product_add():
    form = ProductForm()
    categories = Category.query.filter_by(is_active=True).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        slug = slugify(form.name.data)
        product = Product(
            name=form.name.data, slug=slug, description=form.description.data,
            features=form.features.data, price=form.price.data,
            discount_price=form.discount_price.data, sku=form.sku.data,
            brand=form.brand.data, category_id=form.category_id.data,
            stock_quantity=form.stock_quantity.data,
            low_stock_threshold=form.low_stock_threshold.data,
            weight=form.weight.data, is_active=form.is_active.data,
            is_featured=form.is_featured.data, is_new_arrival=form.is_new_arrival.data,
            is_bestseller=form.is_bestseller.data
        )
        if form.discount_price.data and form.discount_price.data < form.price.data:
            product.discount_percent = round((1 - form.discount_price.data / form.price.data) * 100, 1)
        db.session.add(product)
        db.session.flush()
        images = request.files.getlist('images')
        for i, img in enumerate(images):
            if img and img.filename:
                path = save_upload(img, 'products')
                if path:
                    pi = ProductImage(product_id=product.id, image_url=path, is_primary=(i==0))
                    db.session.add(pi)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', form=form, title='Add Product')


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    categories = Category.query.filter_by(is_active=True).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        product.name = form.name.data
        product.slug = slugify(form.name.data)
        product.description = form.description.data
        product.features = form.features.data
        product.price = form.price.data
        product.discount_price = form.discount_price.data
        product.sku = form.sku.data
        product.brand = form.brand.data
        product.category_id = form.category_id.data
        product.stock_quantity = form.stock_quantity.data
        product.low_stock_threshold = form.low_stock_threshold.data
        product.weight = form.weight.data
        product.is_active = form.is_active.data
        product.is_featured = form.is_featured.data
        product.is_new_arrival = form.is_new_arrival.data
        product.is_bestseller = form.is_bestseller.data
        if product.discount_price and product.discount_price < product.price:
            product.discount_percent = round((1 - product.discount_price / product.price) * 100, 1)
        else:
            product.discount_percent = 0
        images = request.files.getlist('images')
        for i, img in enumerate(images):
            if img and img.filename:
                path = save_upload(img, 'products')
                if path:
                    pi = ProductImage(product_id=product.id, image_url=path, is_primary=(not product.images.first()))
                    db.session.add(pi)
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    elif request.method == 'GET':
        form.category_id.data = product.category_id
    return render_template('admin/product_form.html', form=form, title='Edit Product', product=product)


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.products'))


# --- CATEGORIES ---
@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_bp.route('/categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def category_form(cat_id=None):
    category = Category.query.get(cat_id) if cat_id else None
    form = CategoryForm(obj=category)
    parents = Category.query.filter_by(parent_id=None).all()
    form.parent_id.choices = [(0, 'None')] + [(c.id, c.name) for c in parents]
    if form.validate_on_submit():
        if category:
            category.name = form.name.data
            category.slug = slugify(form.name.data)
            category.description = form.description.data
            category.parent_id = form.parent_id.data if form.parent_id.data else None
            category.is_active = form.is_active.data
            category.sort_order = form.sort_order.data
        else:
            category = Category(
                name=form.name.data, slug=slugify(form.name.data),
                description=form.description.data,
                parent_id=form.parent_id.data if form.parent_id.data else None,
                is_active=form.is_active.data, sort_order=form.sort_order.data
            )
            db.session.add(category)
        if form.image.data:
            path = save_upload(form.image.data, 'categories')
            if path:
                category.image = path
        db.session.commit()
        flash('Category saved!', 'success')
        return redirect(url_for('admin.categories'))
    elif request.method == 'GET':
        form.parent_id.data = category.parent_id if category else 0
    return render_template('admin/category_form.html', form=form, category=category)


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def category_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories'))


# --- ORDERS ---
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Order.order_number.ilike(f'%{search}%'))
    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/orders.html', orders=orders, current_status=status, search=search)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm()
    if form.validate_on_submit():
        old = order.status
        order.status = form.status.data
        h = OrderStatusHistory(order_id=order.id, old_status=old, new_status=form.status.data,
                               note=form.note.data, updated_by=current_user.id)
        db.session.add(h)
        n = Notification(user_id=order.user_id, title='Order Updated',
                         message=f'Order {order.order_number} is now {form.status.data}.',
                         notification_type='info', link=f'/customer/orders/{order.id}')
        db.session.add(n)
        db.session.commit()
        flash('Order status updated.', 'success')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    form.status.data = order.status
    history = OrderStatusHistory.query.filter_by(order_id=order.id).order_by(OrderStatusHistory.created_at).all()
    return render_template('admin/order_detail.html', order=order, form=form,
                         history=history, status_color=get_status_color)


# --- PAYMENTS ---
@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/payments.html', payments=payments)


@admin_bp.route('/payments/<int:payment_id>/verify', methods=['GET', 'POST'])
@login_required
@admin_required
def verify_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    form = PaymentVerificationForm()
    if form.validate_on_submit():
        payment.status = form.status.data
        payment.verified_by = current_user.id
        payment.verified_at = datetime.utcnow()
        if payment.proof:
            payment.proof.status = form.status.data
            payment.proof.verification_note = form.verification_note.data
            payment.proof.rejection_reason = form.rejection_reason.data
        if form.status.data == 'VERIFIED':
            payment.order.payment_status = 'VERIFIED'
            n = Notification(user_id=payment.order.user_id, title='Payment Approved',
                             message=f'Payment for order {payment.order.order_number} has been verified.',
                             notification_type='success', link=f'/customer/orders/{payment.order.id}')
        else:
            payment.order.payment_status = 'REJECTED'
            n = Notification(user_id=payment.order.user_id, title='Payment Rejected',
                             message=f'Payment for order {payment.order.order_number} was rejected.',
                             notification_type='danger', link=f'/customer/orders/{payment.order.id}')
        db.session.add(n)
        db.session.commit()
        flash('Payment verification updated.', 'success')
        return redirect(url_for('admin.payments'))
    return render_template('admin/verify_payment.html', payment=payment, form=form)


# --- SERVICES ---
@admin_bp.route('/services')
@login_required
@admin_required
def services():
    services = Service.query.order_by(Service.sort_order).all()
    return render_template('admin/services.html', services=services)


@admin_bp.route('/services/add', methods=['GET', 'POST'])
@admin_bp.route('/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def service_form(service_id=None):
    service = Service.query.get(service_id) if service_id else None
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        if service:
            service.name = form.name.data
            service.slug = slugify(form.name.data)
            service.description = form.description.data
            service.features = form.features.data
            service.fee = form.fee.data
            service.estimated_duration = form.estimated_duration.data
            service.is_active = form.is_active.data
            service.sort_order = form.sort_order.data
        else:
            service = Service(name=form.name.data, slug=slugify(form.name.data),
                             description=form.description.data, features=form.features.data,
                             fee=form.fee.data, estimated_duration=form.estimated_duration.data,
                             is_active=form.is_active.data, sort_order=form.sort_order.data)
            db.session.add(service)
        if form.image.data:
            path = save_upload(form.image.data, 'services')
            if path:
                service.image = path
        db.session.commit()
        flash('Service saved!', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/service_form.html', form=form, service=service)


@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
@admin_required
def service_delete(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service deleted.', 'success')
    return redirect(url_for('admin.services'))


# --- APPOINTMENTS ---
@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = ServiceBooking.query
    if status:
        query = query.filter_by(status=status)
    appts = query.order_by(ServiceBooking.created_at.desc()).paginate(page=page, per_page=15)
    technicians = Technician.query.all()
    return render_template('admin/appointments.html', appointments=appts,
                         technicians=technicians, current_status=status)


@admin_bp.route('/appointments/<int:appt_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def appointment_detail(appt_id):
    booking = ServiceBooking.query.get_or_404(appt_id)
    form = ServiceStatusForm()
    technicians = Technician.query.filter_by(is_available=True).all()
    form.technician_id.choices = [(0, 'None')] + [(t.id, t.user.full_name) for t in technicians]
    if form.validate_on_submit():
        old = booking.status
        booking.status = form.status.data
        if form.technician_id.data and form.technician_id.data != 0:
            booking.technician_id = form.technician_id.data
        h = AppointmentStatusHistory(booking_id=booking.id, old_status=old,
                                     new_status=form.status.data, note=form.note.data,
                                     updated_by=current_user.id)
        db.session.add(h)
        n = Notification(user_id=booking.user_id, title='Appointment Updated',
                         message=f'Booking {booking.booking_number} is now {form.status.data}.',
                         notification_type='info', link=f'/customer/appointments/{booking.id}')
        db.session.add(n)
        db.session.commit()
        flash('Appointment updated.', 'success')
        return redirect(url_for('admin.appointment_detail', appt_id=appt_id))
    form.status.data = booking.status
    form.technician_id.data = booking.technician_id or 0
    history = AppointmentStatusHistory.query.filter_by(booking_id=booking.id).order_by(AppointmentStatusHistory.created_at).all()
    return render_template('admin/appointment_detail.html', booking=booking, form=form,
                         history=history, status_color=get_status_color)


# --- TECHNICIANS ---
@admin_bp.route('/technicians')
@login_required
@admin_required
def technicians():
    techs = Technician.query.all()
    return render_template('admin/technicians.html', technicians=techs)


@admin_bp.route('/technicians/add', methods=['GET', 'POST'])
@admin_bp.route('/technicians/<int:tech_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def technician_form(tech_id=None):
    tech = Technician.query.get(tech_id) if tech_id else None
    form = TechnicianForm(obj=tech)
    users = User.query.filter(~User.roles.any(Role.name.in_(['admin', 'staff', 'technician']))).all()
    form.user_id.choices = [(u.id, u.full_name) for u in users]
    if form.validate_on_submit():
        if tech:
            tech.skills = form.skills.data
            tech.experience_years = form.experience_years.data
            tech.bio = form.bio.data
            tech.hourly_rate = form.hourly_rate.data
            tech.is_available = form.is_available.data
        else:
            tech = Technician(user_id=form.user_id.data, skills=form.skills.data,
                             experience_years=form.experience_years.data, bio=form.bio.data,
                             hourly_rate=form.hourly_rate.data, is_available=form.is_available.data)
            db.session.add(tech)
            user = User.query.get(form.user_id.data)
            tech_role = Role.query.filter_by(name='technician').first()
            if tech_role and tech_role not in user.roles:
                user.roles.append(tech_role)
        db.session.commit()
        flash('Technician saved!', 'success')
        return redirect(url_for('admin.technicians'))
    return render_template('admin/technician_form.html', form=form, tech=tech)


# --- STAFF ---
@admin_bp.route('/staff')
@login_required
@admin_required
def staff_list():
    users = User.query.join(User.roles).filter(Role.name.in_(['staff', 'technician'])).all()
    return render_template('admin/staff.html', staff_users=users)


@admin_bp.route('/staff/add', methods=['GET', 'POST'])
@login_required
@admin_required
def staff_add():
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    first_name=form.first_name.data, last_name=form.last_name.data,
                    phone=form.phone.data)
        user.set_password('password123')
        role = Role.query.filter_by(name=form.role.data).first()
        if role:
            user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        flash(f'Staff added. Default password: password123', 'success')
        return redirect(url_for('admin.staff_list'))
    return render_template('admin/staff_form.html', form=form)


# --- REVIEWS ---
@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    flash('Review approved.', 'success')
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('admin.reviews'))


# --- MESSAGES ---
@admin_bp.route('/messages')
@login_required
@admin_required
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/messages/<int:msg_id>/read', methods=['POST'])
@login_required
@admin_required
def read_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True})


# --- ANNOUNCEMENTS ---
@admin_bp.route('/announcements')
@login_required
@admin_required
def announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=anns)


@admin_bp.route('/announcements/add', methods=['GET', 'POST'])
@admin_bp.route('/announcements/<int:ann_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def announcement_form(ann_id=None):
    ann = Announcement.query.get(ann_id) if ann_id else None
    form = AnnouncementForm(obj=ann)
    if form.validate_on_submit():
        if ann:
            ann.title = form.title.data
            ann.content = form.content.data
            ann.announcement_type = form.announcement_type.data
            ann.is_active = form.is_active.data
            ann.is_pinned = form.is_pinned.data
            ann.target_audience = form.target_audience.data
        else:
            ann = Announcement(title=form.title.data, content=form.content.data,
                              announcement_type=form.announcement_type.data,
                              is_active=form.is_active.data, is_pinned=form.is_pinned.data,
                              target_audience=form.target_audience.data,
                              created_by=current_user.id)
            db.session.add(ann)
        db.session.commit()
        flash('Announcement saved!', 'success')
        return redirect(url_for('admin.announcements'))
    return render_template('admin/announcement_form.html', form=form, announcement=ann)


# --- BANNERS ---
@admin_bp.route('/banners')
@login_required
@admin_required
def banners():
    banners = Banner.query.order_by(Banner.sort_order).all()
    return render_template('admin/banners.html', banners=banners)


@admin_bp.route('/banners/add', methods=['GET', 'POST'])
@admin_bp.route('/banners/<int:banner_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def banner_form(banner_id=None):
    banner = Banner.query.get(banner_id) if banner_id else None
    form = BannerForm(obj=banner)
    if form.validate_on_submit():
        if banner:
            banner.title = form.title.data
            banner.description = form.description.data
            banner.button_text = form.button_text.data
            banner.button_url = form.button_url.data
            banner.position = form.position.data
            banner.is_active = form.is_active.data
            banner.sort_order = form.sort_order.data
        else:
            banner = Banner(title=form.title.data, description=form.description.data,
                           button_text=form.button_text.data, button_url=form.button_url.data,
                           position=form.position.data, is_active=form.is_active.data,
                           sort_order=form.sort_order.data)
            db.session.add(banner)
        if form.image.data:
            path = save_upload(form.image.data, 'banners')
            if path:
                banner.image_url = path
        db.session.commit()
        flash('Banner saved!', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banner_form.html', form=form, banner=banner)


# --- SETTINGS ---
@admin_bp.route('/payment-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def payment_settings():
    ps = PaymentSettings.get_active() or PaymentSettings()
    form = PaymentSettingsForm(obj=ps)
    if form.validate_on_submit():
        ps.bank_name = form.bank_name.data
        ps.account_title = form.account_title.data
        ps.account_number = form.account_number.data
        ps.iban = form.iban.data
        ps.mobile_wallet_name = form.mobile_wallet_name.data
        ps.mobile_wallet_number = form.mobile_wallet_number.data
        ps.instructions = form.instructions.data
        db.session.add(ps)
        db.session.commit()
        flash('Payment settings saved!', 'success')
        return redirect(url_for('admin.payment_settings'))
    return render_template('admin/payment_settings.html', form=form)
