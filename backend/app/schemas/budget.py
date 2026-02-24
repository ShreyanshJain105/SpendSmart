"""Marshmallow schemas for Budget."""
import re

from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE


def _valid_month(value: str) -> None:
    """Validate that month is in YYYY-MM format."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValidationError("month must be in YYYY-MM format (e.g. 2024-03)")


class BudgetSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    category_id = fields.Int(required=True)
    month = fields.Str(
        required=True,
        validate=_valid_month,
    )
    limit_amount = fields.Decimal(
        required=True,
        places=2,
        as_string=False,
        validate=validate.Range(min=0.01, error="limit_amount must be greater than 0"),
    )
    category = fields.Dict(dump_only=True, allow_none=True)


class BudgetUpdateSchema(BudgetSchema):
    category_id = fields.Int(required=False)
    month = fields.Str(required=False, validate=_valid_month)
    limit_amount = fields.Decimal(
        required=False,
        places=2,
        as_string=False,
        validate=validate.Range(min=0.01),
    )
