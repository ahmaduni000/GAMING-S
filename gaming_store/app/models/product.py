from datetime import datetime
from app import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255), default='default_category.png')
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy='dynamic')
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, default=0.0)
    discount_price = db.Column(db.Float)
    discount_percent = db.Column(db.Float, default=0.0)
    sku = db.Column(db.String(50), unique=True)
    brand = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    weight = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_new_arrival = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    total_sales = db.Column(db.Integer, default=0)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    specifications = db.relationship('ProductSpecification', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    inventory_records = db.relationship('Inventory', backref='product', lazy='dynamic')

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_on_sale(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_percent_calc(self):
        """Calculate discount percentage from price and discount_price.
        Falls back to the stored discount_percent if prices aren't set."""
        if self.price and self.discount_price and self.discount_price < self.price:
            return round(((self.price - self.discount_price) / self.price) * 100)
        if self.discount_percent:
            return int(self.discount_percent)
        return 0

    @property
    def primary_image(self):
        img = self.images.filter_by(is_primary=True).first()
        if img:
            return img.image_url
        img = self.images.first()
        if img:
            return img.image_url
        return '/static/images/default_product.svg'

    def __repr__(self):
        return f'<Product {self.name}>'


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductImage {self.product_id}>'


class ProductSpecification(db.Model):
    __tablename__ = 'product_specifications'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    spec_name = db.Column(db.String(100), nullable=False)
    spec_value = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ProductSpecification {self.spec_name}: {self.spec_value}>'


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updater = db.relationship('User', backref='inventory_updates')

    def __repr__(self):
        return f'<Inventory {self.product_id}: {self.quantity_change}>'
