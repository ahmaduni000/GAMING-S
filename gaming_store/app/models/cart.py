from datetime import datetime
from app import db


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_discount(self):
        return sum(item.discount_amount for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()

    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref='cart_items')

    @property
    def subtotal(self):
        return self.product.effective_price * self.quantity

    @property
    def discount_amount(self):
        if self.product.is_on_sale:
            return (self.product.price - self.product.discount_price) * self.quantity
        return 0

    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'


class Wishlist(db.Model):
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('WishlistItem', backref='wishlist', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Wishlist {self.id}>'


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'

    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='wishlist_items')

    def __repr__(self):
        return f'<WishlistItem {self.product_id}>'
