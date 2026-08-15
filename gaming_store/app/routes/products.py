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
from app.utils.helpers import generate_order_number, format_currency
from app.utils.decorators import customer_required
from datetime import datetime

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
def listing():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    query = Product.query.filter_by(is_active=True)

    # Search
    search = request.args.get('q', '')
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    # Category filter
    category_id = request.args.get('category', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Brand filter
    brand = request.args.get('brand', '')
    if brand:
        query = query.filter(Product.brand.ilike(f'%{brand}%'))

    # Price filter
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)

    # Rating filter
    min_rating = request.args.get('rating', type=float)
    if min_rating:
        query = query.filter(Product.rating >= min_rating)

    # Stock filter
    in_stock = request.args.get('in_stock')
    if in_stock:
        query = query.filter(Product.stock_quantity > 0)

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.total_sales.desc())
    elif sort == 'discount':
        query = query.order_by(Product.discount_percent.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.filter_by(is_active=True, parent_id=None).all()
    brands = db.session.query(Product.brand).filter(Product.brand.isnot(None)).distinct().all()
    brands = [b[0] for b in brands if b[0]]

    return render_template('main/products.html',
                         products=products, categories=categories,
                         brands=brands, search=search,
                         current_category=category_id, current_sort=sort)


@products_bp.route('/<slug>')
def detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()
    related = Product.query.filter_by(category_id=product.category_id, is_active=True).filter(Product.id != product.id).limit(4).all()
    review_form = ReviewForm()

    in_wishlist = False
    if current_user.is_authenticated and current_user.wishlist:
        in_wishlist = WishlistItem.query.filter_by(
            wishlist_id=current_user.wishlist.id, product_id=product.id
        ).first() is not None

    return render_template('main/product_detail.html',
                         product=product, reviews=reviews,
                         related=related, review_form=review_form,
                         in_wishlist=in_wishlist)


@products_bp.route('/cart')
@login_required
def cart():
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart_obj:
        cart_obj = Cart(user_id=current_user.id)
        db.session.add(cart_obj)
        db.session.commit()
    items = CartItem.query.filter_by(cart_id=cart_obj.id).all()
    total = sum(item.subtotal for item in items)
    total_discount = sum(item.discount_amount for item in items)
    delivery_fee = 200 if total > 0 else 0
    final_total = total + delivery_fee
    return render_template('main/cart.html', cart=cart_obj, items=items,
                         total=total, total_discount=total_discount,
                         delivery_fee=delivery_fee, final_total=final_total)


@products_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    product = Product.query.get_or_404(product_id)
    if product.stock_quantity < quantity:
        flash('Insufficient stock.', 'danger')
        return redirect(url_for('products.detail', slug=product.slug))
    cart_obj = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart_obj:
        cart_obj = Cart(user_id=current_user.id)
        db.session.add(cart_obj)
        db.session.flush()
    item = CartItem.query.filter_by(cart_id=cart_obj.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart_obj.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('products.cart'))


@products_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('products.cart'))
    quantity = request.form.get('quantity', 1, type=int)
    if quantity <= 0:
        db.session.delete(item)
    else:
        if item.product.stock_quantity < quantity:
            flash('Insufficient stock.', 'danger')
            return redirect(url_for('products.cart'))
        item.quantity = quantity
    db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('products.cart'))


@products_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.cart.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('products.cart'))
    db.session.delete(item)
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

    payment_method = request.form.get('payment_method', 'cod')

    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        subtotal=total,
        discount=total_discount,
        delivery_fee=delivery_fee,
        total=final_total,
        payment_method=payment_method,
        payment_status='PENDING',
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
