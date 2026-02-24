"""Transactions blueprint — thin HTTP layer, delegates to TransactionService."""
import datetime

import structlog
from flask import Blueprint, jsonify, request

from app.schemas.transaction import TransactionSchema, TransactionUpdateSchema
from app.services.transaction_service import TransactionService

log = structlog.get_logger()
transactions_bp = Blueprint("transactions", __name__)

_schema = TransactionSchema()
_update_schema = TransactionUpdateSchema()


@transactions_bp.route("", methods=["GET"])
def list_transactions():
    type_filter = request.args.get("type")
    category_id = request.args.get("category_id", type=int)
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    try:
        date_from = datetime.date.fromisoformat(date_from_str) if date_from_str else None
        date_to = datetime.date.fromisoformat(date_to_str) if date_to_str else None
    except ValueError as exc:
        return jsonify({"error": f"Invalid date format: {exc}", "code": 400}), 400

    records, total = TransactionService.get_all(
        type_filter=type_filter,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        limit=min(limit, 200),  # hard cap to prevent runaway queries
        offset=offset,
    )
    return jsonify({
        "data": [t.to_dict() for t in records],
        "total": total,
        "limit": limit,
        "offset": offset,
    }), 200


@transactions_bp.route("", methods=["POST"])
def create_transaction():
    payload = _schema.load(request.get_json(force=True) or {})
    t = TransactionService.create(**payload)
    return jsonify(t.to_dict()), 201


@transactions_bp.route("/<int:transaction_id>", methods=["GET"])
def get_transaction(transaction_id: int):
    t = TransactionService.get_by_id(transaction_id)
    return jsonify(t.to_dict()), 200


@transactions_bp.route("/<int:transaction_id>", methods=["PUT"])
def update_transaction(transaction_id: int):
    payload = _update_schema.load(request.get_json(force=True) or {})
    t = TransactionService.update(transaction_id, payload)
    return jsonify(t.to_dict()), 200


@transactions_bp.route("/<int:transaction_id>", methods=["DELETE"])
def delete_transaction(transaction_id: int):
    TransactionService.delete(transaction_id)
    return jsonify({"message": "Deleted"}), 200
