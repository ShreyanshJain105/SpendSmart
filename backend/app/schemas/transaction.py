"""Marshmallow schemas for Transaction."""
import datetime

from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE


VALID_TYPES = ("income", "expense")


class TransactionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=False,
        validate=validate.Range(min=0.01, error="amount must be greater than 0"),
    )
    type = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_TYPES, error="type must be 'income' or 'expense'"),
    )
    date = fields.Date(
        load_default=datetime.date.today,
        format="%Y-%m-%d",
    )
    description = fields.Str(
        load_default="",
        validate=validate.Length(max=256),
    )
    category_id = fields.Int(load_default=None, allow_none=True)

    # Nested read-only representation (populated when serialising)
    category = fields.Dict(dump_only=True, allow_none=True)


class TransactionUpdateSchema(TransactionSchema):
    """All fields optional for partial updates."""
    amount = fields.Decimal(
        required=False,
        places=2,
        as_string=False,
        validate=validate.Range(min=0.01),
    )
    type = fields.Str(
        required=False,
        validate=validate.OneOf(VALID_TYPES),
    )
