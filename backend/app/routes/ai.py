"""AI categorization blueprint."""
from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, validate, EXCLUDE, ValidationError

from app.services.ai_service import suggest_category

ai_bp = Blueprint("ai", __name__)


class _CategorizeRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    description = fields.Str(required=True, validate=validate.Length(min=1, max=256))


_req_schema = _CategorizeRequestSchema()


@ai_bp.route("/categorize", methods=["POST"])
def categorize():
    payload = _req_schema.load(request.get_json(force=True) or {})
    result = suggest_category(payload["description"])
    return jsonify(result), 200
