"""Budgets blueprint."""
import structlog
from flask import Blueprint, jsonify, request

from app.schemas.budget import BudgetSchema, BudgetUpdateSchema
from app.services.budget_service import BudgetService

log = structlog.get_logger()
budgets_bp = Blueprint("budgets", __name__)

_schema = BudgetSchema()
_update_schema = BudgetUpdateSchema()


@budgets_bp.route("", methods=["GET"])
def list_budgets():
    month = request.args.get("month")
    if month:
        # Return budgets with actuals computation
        data = BudgetService.get_with_actuals(month)
        return jsonify(data), 200
    budgets = BudgetService.get_all()
    return jsonify([b.to_dict() for b in budgets]), 200


@budgets_bp.route("", methods=["POST"])
def create_budget():
    payload = _schema.load(request.get_json(force=True) or {})
    b = BudgetService.create(**payload)
    return jsonify(b.to_dict()), 201


@budgets_bp.route("/<int:budget_id>", methods=["GET"])
def get_budget(budget_id: int):
    b = BudgetService.get_by_id(budget_id)
    return jsonify(b.to_dict()), 200


@budgets_bp.route("/<int:budget_id>", methods=["PUT"])
def update_budget(budget_id: int):
    payload = _update_schema.load(request.get_json(force=True) or {})
    b = BudgetService.update(budget_id, payload)
    return jsonify(b.to_dict()), 200


@budgets_bp.route("/<int:budget_id>", methods=["DELETE"])
def delete_budget(budget_id: int):
    BudgetService.delete(budget_id)
    return jsonify({"message": "Deleted"}), 200
