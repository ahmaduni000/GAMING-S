from datetime import datetime
from app import db


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_replied = db.Column(db.Boolean, default=False)
    reply = db.Column(db.Text)
    replied_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replier = db.relationship('User', backref='replied_messages')

    def __repr__(self):
        return f'<ContactMessage {self.subject}>'


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    announcement_type = db.Column(db.String(30), default='info')  # info, warning, success, promotion
    is_active = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    target_audience = db.Column(db.String(30), default='all')  # all, customers, staff
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', backref='announcements_created')

    def __repr__(self):
        return f'<Announcement {self.title}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30), default='info')
    link = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.title}>'


class Banner(db.Model):
    __tablename__ = 'banners'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(500))
    position = db.Column(db.String(50), default='hero')  # hero, promo, sidebar, footer
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Banner {self.title}>'


class Advertisement(db.Model):
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    link_url = db.Column(db.String(500))
    position = db.Column(db.String(50), default='sidebar')  # sidebar, homepage, footer, popup
    is_active = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Advertisement {self.title}>'


class HomepageContent(db.Model):
    __tablename__ = 'homepage_content'

    id = db.Column(db.Integer, primary_key=True)
    # Hero section
    hero_title = db.Column(db.String(300), default='Level Up Your Gaming Experience')
    hero_subtitle = db.Column(db.Text, default='Discover the latest gaming PCs, consoles, accessories, and professional gaming services.')
    hero_badge = db.Column(db.String(100), default='Welcome to GameZone')
    hero_button1_text = db.Column(db.String(50), default='Shop Now')
    hero_button1_url = db.Column(db.String(200), default='/products')
    hero_button2_text = db.Column(db.String(50), default='Our Services')
    hero_button2_url = db.Column(db.String(200), default='/services')
    # Section headings
    categories_title = db.Column(db.String(200), default='Shop by Category')
    categories_subtitle = db.Column(db.String(300), default='Find exactly what you need across our curated categories')
    featured_title = db.Column(db.String(200), default='Featured Products')
    discount_title = db.Column(db.String(200), default='Discounted Products')
    services_title = db.Column(db.String(200), default='Professional Gaming Services')
    services_subtitle = db.Column(db.String(300), default='Expert technicians for all your gaming needs')
    cta_title = db.Column(db.String(200), default='Ready to Level Up?')
    cta_subtitle = db.Column(db.String(300), default='Join thousands of gamers who trust GameZone for their gaming needs.')
    cta_button1_text = db.Column(db.String(50), default='Create Account')
    cta_button1_url = db.Column(db.String(200), default='/auth/register')
    cta_button2_text = db.Column(db.String(50), default='Contact Us')
    cta_button2_url = db.Column(db.String(200), default='/contact')
    show_featured = db.Column(db.Boolean, default=True)
    show_discount = db.Column(db.Boolean, default=True)
    show_services = db.Column(db.Boolean, default=True)
    show_categories = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        settings = HomepageContent.query.first()
        if not settings:
            settings = HomepageContent()
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self):
        return f'<HomepageContent {self.id}>'
