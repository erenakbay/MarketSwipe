from flask_jwt_extended import current_user, jwt_required
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from marshmallow import EXCLUDE, fields
from app import CamelCaseSchema, SQLAlchemyAutoCamelCaseSchema, db, ma
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

from products import Product

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


class CartProduct(db.Model):
    """
    Model representing a product in the user's cart.
    """
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), primary_key=True, nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship("User", backref="cart_product")
    product = db.relationship("Product", backref="cart_product")
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )


class CartProductSchema(SQLAlchemyAutoCamelCaseSchema):
    class Meta:
        model = CartProduct
        include_relationships = True
        load_instance = True


class ProductRequestSchema(CamelCaseSchema):
    """
    Schema for validating product request data.
    """
    product_id = fields.Integer(required=True, strict=True)
    quantity = fields.Integer(strict=True, load_default=1)

    class Meta:
        unknown = EXCLUDE


@cart_bp.route("/", methods=["GET"])
@jwt_required()
def get_cart():
    """
    Retrieves the current user's cart.
    """
    cart = (
        CartProduct.query.join(Product, CartProduct.product_id == Product.id)
        .filter(CartProduct.user_id == current_user.id)
        .all()
    )
    return jsonify(CartProductSchema().dump(cart, many=True)), 200


@cart_bp.route("/add", methods=["POST"])
@jwt_required()
def add_cart_product():
    """
    Adds a product to the user's cart.
    """
    data = ProductRequestSchema().load(request.get_json())
    product_id = data["product_id"]
    if not Product.query.get(product_id):
        return {"message": "Product not found"}, 404
    cart_product = CartProduct.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()
    if cart_product:
        cart_product.quantity += data["quantity"]
    else:
        cart_product = CartProduct(
            user_id=current_user.id,
            product_id=product_id,
            quantity=data["quantity"],
        )
        db.session.add(cart_product)
    db.session.commit()
    return {"message": "Product successfully added to cart"}, 200


@cart_bp.route("/remove", methods=["POST"])
@jwt_required()
def remove_cart_product():
    """
    Removes a product from the user's cart.
    """
    data = request.get_json()
    product_id = data.get("productId")
    if not product_id:
        return {"message": "productId is required"}, 400
    product = CartProduct.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()
    if not product:
        return {"message": "Product not in cart"}, 403
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product successfully removed from cart"}, 200
