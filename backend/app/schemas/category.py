"""Marshmallow schemas for Category.

Schemas are the boundary guards — they validate and deserialize request data
before it reaches any service.  All validation errors surface as 422 responses
(handled by the global error handler), never as 500s.
"""
from marshmallow import Schema, fields, validate, EXCLUDE


class CategorySchema(Schema):
    """Full representation (used for serialization and responses)."""

    class Meta:
        # Ignore unknown keys — adding new fields to the model won't break
        # existing API clients.
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=64),
    )
    icon = fields.Str(
        load_default="💰",
        validate=validate.Length(min=1, max=8),
    )
    color = fields.Str(
        load_default="#6366f1",
        validate=validate.Regexp(
            r"^#[0-9a-fA-F]{6}$",
            error="color must be a valid hex color (e.g. #ff5733)",
        ),
    )


class CategoryUpdateSchema(CategorySchema):
    """For PATCH/PUT — name is optional so clients can update a single field."""
    name = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=64),
    )
