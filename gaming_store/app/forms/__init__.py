from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (StringField, PasswordField, TextAreaField, IntegerField,
                     FloatField, SelectField, BooleanField, DateTimeField, DateField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo, Optional,
                                 NumberRange, ValidationError)
from app.models.user import User
from app.utils.helpers import (
    PAYMENT_COD, PAYMENT_BANK, PAYMENT_EASYPAISA, PAYMENT_JAZZCASH,
    PAYMENT_METHOD_LABELS
)

# Payment method choices shared across forms
PAYMENT_METHOD_CHOICES = [
    (PAYMENT_COD, PAYMENT_METHOD_LABELS[PAYMENT_COD]),
    (PAYMENT_BANK, PAYMENT_METHOD_LABELS[PAYMENT_BANK]),
    (PAYMENT_EASYPAISA, PAYMENT_METHOD_LABELS[PAYMENT_EASYPAISA]),
    (PAYMENT_JAZZCASH, PAYMENT_METHOD_LABELS[PAYMENT_JAZZCASH]),
]


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(6)])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(), EqualTo('new_password')])


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional(), Length(2, 100)])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(2, 100)])
    username = StringField('Username', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    subject = StringField('Subject', validators=[DataRequired(), Length(5, 200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(10, 2000)])


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    is_active = BooleanField('Active', default=True)
    sort_order = IntegerField('Sort Order', default=0)


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(2, 200)])
    description = TextAreaField('Description', validators=[Optional()])
    features = TextAreaField('Features', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    discount_price = FloatField('Discount Price', validators=[Optional(), NumberRange(min=0)])
    sku = StringField('SKU', validators=[Optional()])
    brand = StringField('Brand', validators=[Optional(), Length(max=100)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    low_stock_threshold = IntegerField('Low Stock Threshold', default=5)
    weight = FloatField('Weight (kg)', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    is_featured = BooleanField('Featured', default=False)
    is_new_arrival = BooleanField('New Arrival', default=False)
    is_bestseller = BooleanField('Bestseller', default=False)
    images = FileField('Product Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ], render_kw={'multiple': True})


class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired(), Length(2, 150)])
    description = TextAreaField('Description', validators=[Optional()])
    features = TextAreaField('Features', validators=[Optional()])
    fee = FloatField('Service Fee', validators=[DataRequired(), NumberRange(min=0)])
    estimated_duration = StringField('Estimated Duration', validators=[Optional()])
    image = FileField('Service Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    is_active = BooleanField('Active', default=True)
    sort_order = IntegerField('Sort Order', default=0)


class ServiceBookingForm(FlaskForm):
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    technician_id = SelectField('Technician', coerce=int, validators=[Optional()])
    booking_date = DateField('Date', validators=[DataRequired()])
    booking_time = SelectField('Time', choices=[
        ('09:00 AM', '09:00 AM'), ('10:00 AM', '10:00 AM'),
        ('11:00 AM', '11:00 AM'), ('12:00 PM', '12:00 PM'),
        ('01:00 PM', '01:00 PM'), ('02:00 PM', '02:00 PM'),
        ('03:00 PM', '03:00 PM'), ('04:00 PM', '04:00 PM'),
        ('05:00 PM', '05:00 PM')
    ], validators=[DataRequired()])
    service_location = StringField('Service Location', validators=[DataRequired(), Length(5, 200)])
    problem_description = TextAreaField('Problem Description', validators=[Optional()])
    payment_method = SelectField('Payment Method', choices=PAYMENT_METHOD_CHOICES,
                                 validators=[DataRequired()])


class OrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'), ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'), ('OUT FOR DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')
    ], validators=[DataRequired()])
    note = TextAreaField('Note', validators=[Optional()])


class ServiceStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('ASSIGNED', 'Assigned'), ('PROCESSING', 'Processing'),
        ('READY', 'Ready'), ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ], validators=[DataRequired()])
    note = TextAreaField('Note', validators=[Optional()])
    technician_id = SelectField('Assign Technician', coerce=int, validators=[Optional()])


class PaymentVerificationForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('VERIFIED', 'Approve'), ('REJECTED', 'Reject')
    ], validators=[DataRequired()])
    verification_note = TextAreaField('Note', validators=[Optional()])
    rejection_reason = TextAreaField('Rejection Reason', validators=[Optional()])


class BannerForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(2, 200)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Banner Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    button_text = StringField('Button Text', validators=[Optional()])
    button_url = StringField('Button URL', validators=[Optional()])
    position = SelectField('Position', choices=[
        ('hero', 'Hero'), ('promo', 'Promotion'),
        ('sidebar', 'Sidebar'), ('footer', 'Footer')
    ])
    is_active = BooleanField('Active', default=True)
    sort_order = IntegerField('Sort Order', default=0)


class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(2, 200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    announcement_type = SelectField('Type', choices=[
        ('info', 'Info'), ('warning', 'Warning'),
        ('success', 'Success'), ('promotion', 'Promotion')
    ])
    is_active = BooleanField('Active', default=True)
    is_pinned = BooleanField('Pinned', default=False)
    target_audience = SelectField('Target', choices=[
        ('all', 'All Users'), ('customers', 'Customers'), ('staff', 'Staff')
    ])


class PaymentSettingsForm(FlaskForm):
    bank_name = StringField('Bank Name', validators=[Optional()])
    account_title = StringField('Account Title', validators=[Optional()])
    account_number = StringField('Account Number', validators=[Optional()])
    iban = StringField('IBAN', validators=[Optional()])
    easypaisa_number = StringField('Easypaisa Number', validators=[Optional()])
    jazzcash_number = StringField('JazzCash Number', validators=[Optional()])
    mobile_wallet_name = StringField('Mobile Wallet Name', validators=[Optional()])
    mobile_wallet_number = StringField('Mobile Wallet Number', validators=[Optional()])
    instructions = TextAreaField('Payment Instructions', validators=[Optional()])


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, '5 Stars'), (4, '4 Stars'), (3, '3 Stars'),
        (2, '2 Stars'), (1, '1 Star')
    ], coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[Optional(), Length(0, 200)])
    comment = TextAreaField('Comment', validators=[Optional(), Length(0, 2000)])


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(2, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(2, 50)])
    phone = StringField('Phone', validators=[Optional(), Length(10, 20)])
    role = SelectField('Role', choices=[
        ('customer', 'Customer'), ('staff', 'Staff'),
        ('technician', 'Technician'), ('admin', 'Admin')
    ])
    is_active = BooleanField('Active', default=True)


class TechnicianForm(FlaskForm):
    user_id = SelectField('User', coerce=int, validators=[DataRequired()])
    profile_image = FileField('Profile Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    skills = StringField('Skills', validators=[Optional()])
    experience_years = IntegerField('Experience (Years)', validators=[Optional(), NumberRange(min=0)])
    bio = TextAreaField('Bio', validators=[Optional()])
    hourly_rate = FloatField('Hourly Rate', validators=[Optional(), NumberRange(min=0)])
    is_available = BooleanField('Available', default=True)
