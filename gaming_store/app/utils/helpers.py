import random
import string
from datetime import datetime


# Payment method identifiers
PAYMENT_COD = 'cod'
PAYMENT_BANK = 'bank_transfer'
PAYMENT_EASYPAISA = 'easypaisa'
PAYMENT_JAZZCASH = 'jazzcash'

# Online payment methods (require proof upload + admin verification)
ONLINE_PAYMENT_METHODS = [PAYMENT_BANK, PAYMENT_EASYPAISA, PAYMENT_JAZZCASH]

# Human-readable labels for each payment method
PAYMENT_METHOD_LABELS = {
    PAYMENT_COD: 'Cash on Delivery',
    PAYMENT_BANK: 'Bank Transfer',
    PAYMENT_EASYPAISA: 'Easypaisa',
    PAYMENT_JAZZCASH: 'JazzCash',
}

# Icon class (Font Awesome) for each payment method
PAYMENT_METHOD_ICONS = {
    PAYMENT_COD: 'fa-money-bill-wave',
    PAYMENT_BANK: 'fa-university',
    PAYMENT_EASYPAISA: 'fa-mobile-alt',
    PAYMENT_JAZZCASH: 'fa-mobile-screen-button',
}


def get_payment_method_label(method):
    """Return a human-readable label for a payment method code."""
    return PAYMENT_METHOD_LABELS.get(method, (method or '').replace('_', ' ').title())


def is_online_payment(method):
    """Return True if the method is an online (transfer/wallet) payment."""
    return method in ONLINE_PAYMENT_METHODS


def generate_order_number():
    """Generate a unique order number."""
    prefix = 'GS'
    nums = ''.join(random.choices(string.digits, k=8))
    return f'{prefix}-{nums}'


def generate_booking_number():
    """Generate a unique booking number."""
    prefix = 'APT'
    nums = ''.join(random.choices(string.digits, k=8))
    return f'{prefix}-{nums}'


def slugify(text):
    """Convert text to slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def format_currency(amount):
    """Format amount as currency."""
    return f'Rs. {amount:,.2f}'


def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    return price * (1 - discount_percent / 100)


def get_order_status_steps():
    """Return order status workflow steps."""
    return [
        'PENDING', 'CONFIRMED', 'PROCESSING', 'PACKED',
        'SHIPPED', 'OUT FOR DELIVERY', 'DELIVERED'
    ]


def get_service_status_steps():
    """Return service status workflow steps."""
    return [
        'PENDING', 'CONFIRMED', 'ASSIGNED',
        'PROCESSING', 'READY', 'COMPLETED'
    ]


def get_status_color(status):
    """Get Bootstrap color class for status."""
    colors = {
        'PENDING': 'warning',
        'CONFIRMED': 'info',
        'PROCESSING': 'primary',
        'PACKED': 'secondary',
        'SHIPPED': 'info',
        'OUT FOR DELIVERY': 'primary',
        'DELIVERED': 'success',
        'CANCELLED': 'danger',
        'ASSIGNED': 'info',
        'READY': 'info',
        'COMPLETED': 'success',
        'VERIFIED': 'success',
        'CONFIRMED': 'success',
        'REJECTED': 'danger',
        'WAITING_FOR_VERIFICATION': 'warning',
    }
    return colors.get(status, 'secondary')


def time_ago(dt):
    """Return human-readable time ago."""
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f'{mins} min{"s" if mins > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    else:
        return dt.strftime('%b %d, %Y')
