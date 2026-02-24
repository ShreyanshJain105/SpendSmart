"""Categories blueprint."""
import structlog
from flask import Blueprint, jsonify, request

from app.schemas.category import CategorySchema, CategoryUpdateSchema
from app.services.category_service import CategoryService

log = structlog.get_logger()
categories_bp = Blueprint("categories", __name__)

_schema = CategorySchema()
_update_schema = CategoryUpdateSchema()


@categories_bp.route("", methods=["GET"])
def list_categories():
    cats = CategoryService.get_all()
    return jsonify([c.to_dict() for c in cats]), 200


@categories_bp.route("", methods=["POST"])
def create_category():
    payload = _schema.load(request.get_json(force=True) or {})
    cat = CategoryService.create(**payload)
    return jsonify(cat.to_dict()), 201


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id: int):
    cat = CategoryService.get_by_id(category_id)
    return jsonify(cat.to_dict()), 200


@categories_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    payload = _update_schema.load(request.get_json(force=True) or {})
    cat = CategoryService.update(category_id, payload)
    return jsonify(cat.to_dict()), 200


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    CategoryService.delete(category_id)
    return jsonify({"message": "Deleted"}), 200
