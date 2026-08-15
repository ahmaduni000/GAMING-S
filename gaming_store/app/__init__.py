import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
cors = CORS()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please log in to access this page.'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload directories exist
    upload_dirs = [
        'products', 'categories', 'services', 'profiles',
        'payments', 'banners', 'reviews'
    ]
    for d in upload_dirs:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], d), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cors.init_app(app)

    # Register CSRF exempt for API routes
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.customer import customer_bp
    app.register_blueprint(customer_bp, url_prefix='/customer')

    from app.routes.staff import staff_bp
    app.register_blueprint(staff_bp, url_prefix='/staff')

    from app.routes.technician import technician_bp
    app.register_blueprint(technician_bp, url_prefix='/technician')

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')

    from app.routes.services import services_bp
    app.register_blueprint(services_bp, url_prefix='/services')

    # Register error handlers
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models import Category, Cart, Wishlist, Notification
        from flask_login import current_user
        categories = Category.query.filter_by(is_active=True).all()
        cart_count = 0
        wishlist_count = 0
        notification_count = 0
        if current_user.is_authenticated:
            if hasattr(current_user, 'customer_cart'):
                cart_count = Cart.query.filter_by(user_id=current_user.id).count()
            if hasattr(current_user, 'wishlist'):
                wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            notification_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(
            site_categories=categories,
            cart_count=cart_count,
            wishlist_count=wishlist_count,
            notification_count=notification_count
        )

    return app
