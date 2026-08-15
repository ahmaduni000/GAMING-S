from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    """Decorator to require specific roles for a view."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if not any(current_user.primary_role == role for role in roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """Decorator to require staff or admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not (current_user.is_staff or current_user.is_admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def technician_required(f):
    """Decorator to require technician role (admin allowed too)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not (current_user.is_technician_role or current_user.is_admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """Decorator to require customer role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_customer and not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def log_activity(action, details=None):
    """Log user activity."""
    from app import db
    from app.models.user import ActivityLog
    import flask
    log = ActivityLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=flask.request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
