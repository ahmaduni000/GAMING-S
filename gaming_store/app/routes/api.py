from flask import Blueprint, jsonify, request
from app.models.product import Product, Category
from app.models.service import Service
from app.models.user import Technician

api_bp = Blueprint('api', __name__)


@api_bp.route('/products/search')
def search_products():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
    products = Product.query.filter(
        Product.name.ilike(f'%{q}%'), Product.is_active == True
    ).limit(10).all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'price': p.price,
        'image': p.primary_image, 'slug': p.slug
    } for p in products])


@api_bp.route('/categories')
def get_categories():
    cats = Category.query.filter_by(is_active=True).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in cats])


@api_bp.route('/services')
def get_services():
    services = Service.query.filter_by(is_active=True).all()
    return jsonify([{'id': s.id, 'name': s.name, 'fee': s.fee} for s in services])


@api_bp.route('/technicians/<int:service_id>')
def get_technicians(service_id):
    techs = Technician.query.filter_by(is_available=True).all()
    return jsonify([{'id': t.id, 'name': t.user.full_name, 'rating': t.rating} for t in techs])
