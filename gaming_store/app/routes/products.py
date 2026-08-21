from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.product import Product, Category, ProductImage
from app.models.cart import Cart, CartItem, Wishlist, WishlistItem
from app.models.order import Order, OrderItem, BillingDetail, Payment, PaymentProof
from app.models.settings import PaymentSettings
from app.models.communication import Notification
from app.forms import ReviewForm
from app.models.review import Review
from app.utils.helpers import (
    generate_order_number, format_currency,
    is_online_payment, PAYMENT_COD
)
from app.utils.decorators import customer_required
from datetime import datetime

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def listing():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'newest')

    query = Product.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if sort == 'price_low':
        query = query.order_by(Product.effective_price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.effective_price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12)
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('main/products.html', products=products,
                         categories=categories, current_category=category_id,
                         search=search, sort=sort)


@products_bp.route('/<slug>')
def detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = Product.query.filter_by(category_id=product.category_id, is_active=True).filter(Product.id != product.id).limit(4).all()
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template('main/product_detail.html', product=product,
                         related=related, reviews=reviews)


@products_bp.route('/cart')
@login_required
def cart():
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    items = cart_obj.items.all() if cart_obj else []
    total = sum(item.subtotal for item in items)
    total_discount = sum(item.discount_amount for item in items)
    delivery_fee = 200
    final_total = total + delivery_fee
    return render_template('main/cart.html', items=items, total=total,
                         total_discount=total_discount, delivery_fee=delivery_fee,
                         final_total=final_total)


@products_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if not product.is_active:
        flash('This product is not available.', 'warning')
        return redirect(url_for('products.detail', slug=product.slug))

    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    if quantity > product.stock_quantity:
        quantity = product.stock_quantity
        flash(f'Only {product.stock_quantity} items in stock.', 'warning')

    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart_obj:
        cart_obj = Cart(user_id=current_user.id)
        db.session.add(cart_obj)
        db.session.flush()

    cart_item = CartItem.query.filter_by(cart_id=cart_obj.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart_obj.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('products.cart'))


@products_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('products.cart'))

    quantity = int(request.form.get('quantity', cart_item.quantity))
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    else:
        if quantity > cart_item.product.stock_quantity:
            quantity = cart_item.product.stock_quantity
            flash(f'Only {cart_item.product.stock_quantity} items in stock.', 'warning')
        cart_item.quantity = quantity
        flash('Cart updated.', 'success')

    db.session.commit()
    return redirect(url_for('products.cart'))


@products_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('products.cart'))
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('products.cart'))


@products_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart_obj or cart_obj.items.count() == 0:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.listing'))
    items = cart_obj.items.all()
    total = sum(item.subtotal for item in items)
    total_discount = sum(item.discount_amount for item in items)
    delivery_fee = 200
    final_total = total + delivery_fee
    payment_settings = PaymentSettings.get_active()
    return render_template('main/checkout.html', items=items, total=total,
                         total_discount=total_discount, delivery_fee=delivery_fee,
                         final_total=final_total, payment_settings=payment_settings)


@products_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart_obj or cart_obj.items.count() == 0:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.listing'))

    items = cart_obj.items.all()
    total = sum(item.subtotal for item in items)
    total_discount = sum(item.discount_amount for item in items)
    delivery_fee = 200
    final_total = total + delivery_fee

    payment_method = request.form.get('payment_method', PAYMENT_COD)
    if payment_method not in (PAYMENT_COD, 'bank_transfer', 'easypaisa', 'jazzcash'):
        payment_method = PAYMENT_COD

    # Online payments start as PENDING (awaiting proof upload + verification)
    payment_status = 'PENDING' if is_online_payment(payment_method) else 'PENDING'

    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        subtotal=total,
        discount=total_discount,
        delivery_fee=delivery_fee,
        total=final_total,
        payment_method=payment_method,
        payment_status=payment_status,
        notes=request.form.get('notes', '')
    )
    db.session.add(order)
    db.session.flush()

    billing = BillingDetail(
        order_id=order.id,
        full_name=request.form.get('full_name', current_user.full_name),
        email=request.form.get('email', current_user.email),
        phone=request.form.get('phone', current_user.phone),
        address=request.form.get('address', current_user.address),
        city=request.form.get('city', current_user.city),
        postal_code=request.form.get('postal_code', ''),
        notes=request.form.get('order_notes', '')
    )
    db.session.add(billing)

    for cart_item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            product_price=cart_item.product.effective_price,
            quantity=cart_item.quantity,
            subtotal=cart_item.subtotal
        )
        db.session.add(order_item)
        cart_item.product.stock_quantity -= cart_item.quantity
        cart_item.product.total_sales += cart_item.quantity

    # Clear cart
    CartItem.query.filter_by(cart_id=cart_obj.id).delete()

    # Create notification
    notif = Notification(
        user_id=current_user.id,
        title='Order Placed',
        message=f'Your order {order.order_number} has been placed successfully.',
        notification_type='success',
        link=f'/customer/orders/{order.id}'
    )
    db.session.add(notif)

    db.session.commit()

    if is_online_payment(payment_method):
        flash(f'Order {order.order_number} placed! Please upload your payment receipt to confirm.', 'success')
    else:
        flash(f'Order {order.order_number} placed successfully!', 'success')
    return redirect(url_for('customer.order_detail', order_id=order.id))


@products_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    wishlist = Wishlist.query.filter_by(user_id=current_user.id).first()
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id)
        db.session.add(wishlist)
        db.session.flush()
    item = WishlistItem.query.filter_by(wishlist_id=wishlist.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        flash('Removed from wishlist.', 'info')
    else:
        item = WishlistItem(wishlist_id=wishlist.id, product_id=product_id)
        db.session.add(item)
        flash('Added to wishlist!', 'success')
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(request.referrer or url_for('products.listing'))


@products_bp.route('/add-review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            product_id=product_id,
            rating=form.rating.data,
            title=form.title.data,
            comment=form.comment.data
        )
        db.session.add(review)
        product.total_reviews += 1
        reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
        total_rating = sum(r.rating for r in reviews) + form.rating.data
        product.rating = round(total_rating / (len(reviews) + 1), 1)
        db.session.commit()
        flash('Review submitted successfully!', 'success')
    return redirect(url_for('products.detail', slug=product.slug))
