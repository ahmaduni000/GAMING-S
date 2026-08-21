from flask import Blueprint, render_template, request
from app.models import Product, Category, Service, Technician, ContactMessage, Banner, Announcement
from app.models.communication import HomepageContent, Advertisement
from app.models.user import User
from app.models.order import Order
from app.forms import ContactForm
from app import db
from flask import flash, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    latest_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    bestseller_products = Product.query.filter_by(is_bestseller=True, is_active=True).limit(8).all()
    discount_products = Product.query.filter(
        Product.discount_price.isnot(None),
        Product.is_active == True,
        Product.discount_price < Product.price
    ).limit(8).all()
    services = Service.query.filter_by(is_active=True).limit(6).all()
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    banners = Banner.query.filter_by(is_active=True, position='hero').order_by(Banner.sort_order).all()
    promo_banners = Banner.query.filter_by(is_active=True, position='promo').order_by(Banner.sort_order).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.is_pinned.desc()).limit(3).all()
    homepage_content = HomepageContent.get_settings()
    advertisements = Advertisement.query.filter_by(is_active=True).all()

    stats = {
        'total_users': User.query.count(),
        'total_orders': Order.query.count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_services': Service.query.filter_by(is_active=True).count(),
        'total_technicians': Technician.query.filter_by(is_available=True).count()
    }

    return render_template('main/home.html',
                         featured_products=featured_products,
                         latest_products=latest_products,
                         bestseller_products=bestseller_products,
                         discount_products=discount_products,
                         services=services,
                         categories=categories,
                         banners=banners,
                         promo_banners=promo_banners,
                         announcements=announcements,
                         stats=stats,
                         homepage_content=homepage_content,
                         advertisements=advertisements)


@main_bp.route('/about')
def about():
    stats = {
        'total_users': User.query.count(),
        'total_orders': Order.query.count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_services': Service.query.filter_by(is_active=True).count(),
        'total_technicians': Technician.query.filter_by(is_available=True).count()
    }
    technicians = Technician.query.filter_by(is_available=True).limit(6).all()
    return render_template('main/about.html', stats=stats, technicians=technicians)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            username=form.username.data if form.username.data else (current_user.username if current_user.is_authenticated else ''),
            email=form.email.data,
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    elif request.method == 'GET' and current_user.is_authenticated:
        form.name.data = current_user.full_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.username.data = current_user.username
    return render_template('main/contact.html', form=form)
