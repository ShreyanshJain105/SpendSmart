"""Tests for Marshmallow schema validation.

These tests exercise the validation layer in isolation — they don't touch the
database or Flask app context.  Fast, deterministic, no side effects.
"""
import pytest
from marshmallow import ValidationError

from app.schemas.category import CategorySchema
from app.schemas.transaction import TransactionSchema
from app.schemas.budget import BudgetSchema


# ---------------------------------------------------------------------------
# CategorySchema
# ---------------------------------------------------------------------------

class TestCategorySchema:
    def test_valid_category(self):
        data = CategorySchema().load({"name": "Food", "icon": "🍔", "color": "#ff5733"})
        assert data["name"] == "Food"
        assert data["color"] == "#ff5733"

    def test_name_required(self):
        with pytest.raises(ValidationError) as exc:
            CategorySchema().load({"icon": "🍔"})
        assert "name" in exc.value.messages

    def test_name_max_length(self):
        with pytest.raises(ValidationError):
            CategorySchema().load({"name": "x" * 65})

    def test_invalid_color_format(self):
        with pytest.raises(ValidationError):
            CategorySchema().load({"name": "Test", "color": "red"})

    def test_valid_color_lowercase(self):
        data = CategorySchema().load({"name": "Test", "color": "#aabbcc"})
        assert data["color"] == "#aabbcc"

    def test_defaults_applied(self):
        data = CategorySchema().load({"name": "Misc"})
        assert data["icon"] == "💰"
        assert data["color"] == "#6366f1"


# ---------------------------------------------------------------------------
# TransactionSchema
# ---------------------------------------------------------------------------

class TestTransactionSchema:
    def test_valid_expense(self):
        data = TransactionSchema().load({
            "amount": "49.99",
            "type": "expense",
            "description": "Grocery run",
        })
        assert float(data["amount"]) == 49.99
        assert data["type"] == "expense"

    def test_amount_required(self):
        with pytest.raises(ValidationError) as exc:
            TransactionSchema().load({"type": "expense"})
        assert "amount" in exc.value.messages

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            TransactionSchema().load({"amount": "0", "type": "expense"})

    def test_negative_amount_rejected(self):
        with pytest.raises(ValidationError):
            TransactionSchema().load({"amount": "-10", "type": "expense"})

    def test_type_required(self):
        with pytest.raises(ValidationError) as exc:
            TransactionSchema().load({"amount": "10"})
        assert "type" in exc.value.messages

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            TransactionSchema().load({"amount": "10", "type": "transfer"})

    def test_income_type_accepted(self):
        data = TransactionSchema().load({"amount": "3000", "type": "income"})
        assert data["type"] == "income"

    def test_description_max_length(self):
        with pytest.raises(ValidationError):
            TransactionSchema().load({
                "amount": "10",
                "type": "expense",
                "description": "x" * 257,
            })

    def test_unknown_fields_ignored(self):
        data = TransactionSchema().load({
            "amount": "10",
            "type": "expense",
            "unknown_field": "should_be_ignored",
        })
        assert "unknown_field" not in data


# ---------------------------------------------------------------------------
# BudgetSchema
# ---------------------------------------------------------------------------

class TestBudgetSchema:
    def test_valid_budget(self):
        data = BudgetSchema().load({
            "category_id": 1,
            "month": "2024-03",
            "limit_amount": "500",
        })
        assert data["month"] == "2024-03"
        assert float(data["limit_amount"]) == 500.0

    def test_month_format_enforced(self):
        with pytest.raises(ValidationError):
            BudgetSchema().load({
                "category_id": 1,
                "month": "03-2024",  # wrong format
                "limit_amount": "500",
            })

    def test_invalid_month_value(self):
        with pytest.raises(ValidationError):
            BudgetSchema().load({
                "category_id": 1,
                "month": "2024-13",  # month 13 doesn't exist
                "limit_amount": "500",
            })

    def test_limit_must_be_positive(self):
        with pytest.raises(ValidationError):
            BudgetSchema().load({
                "category_id": 1,
                "month": "2024-03",
                "limit_amount": "0",
            })

    def test_category_id_required(self):
        with pytest.raises(ValidationError) as exc:
            BudgetSchema().load({"month": "2024-03", "limit_amount": "100"})
        assert "category_id" in exc.value.messages
