from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.user import User, Role
from app.models.cart import Cart, Wishlist
from app.forms import LoginForm, RegisterForm, ChangePasswordForm, ProfileForm
from app.utils.file_upload import save_upload
from app.utils.decorators import log_activity
from datetime import datetime

auth_bp = Blueprint('auth', 'name')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin-specific login page."""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.admin_login'))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login', f'User {user.username} logged in as admin')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('admin/admin_login.html', form=form)


@auth_bp.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    """Staff-specific login page."""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.staff_login'))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login', f'User {user.username} logged in as staff')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('staff.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('staff/login.html', form=form)


@auth_bp.route('/technician/login', methods=['GET', 'POST'])
def technician_login():
    """Technician-specific login page."""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.technician_login'))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login', f'User {user.username} logged in as technician')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('technician.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('technician/technician_login.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """General customer login page."""
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_activity('login', f'User {user.username} logged in')
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(get_dashboard_url())
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(get_dashboard_url())
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)

        customer_role = Role.query.filter_by(name='customer').first()
        if customer_role:
            user.roles.append(customer_role)

        db.session.add(user)
        db.session.flush()

        cart = Cart(user_id=user.id)
        wishlist = Wishlist(user_id=user.id)
        db.session.add(cart)
        db.session.add(wishlist)
        db.session.commit()

        log_activity('register', f'New user registered: {user.username}')
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    log_activity('logout', f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        if form.profile_image.data:
            image_path = save_upload(form.profile_image.data, 'profiles')
            if image_path:
                current_user.profile_image = image_path
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/change_password.html', form=form)


def get_dashboard_url():
    """Get the appropriate dashboard URL based on user role."""
    if current_user.is_admin:
        return url_for('admin.dashboard')
    elif current_user.is_staff:
        return url_for('staff.dashboard')
    elif current_user.is_technician_role:
        return url_for('technician.dashboard')
    else:
        return url_for('customer.dashboard')
