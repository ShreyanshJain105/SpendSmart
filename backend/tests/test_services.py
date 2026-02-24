"""
Service-layer tests.

These tests call the services directly (no HTTP), so failures point
straight to business logic rather than routing/serialization.
"""
import datetime
import pytest

from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.services.transaction_service import TransactionService
from app.services.category_service import CategoryService
from app.services.budget_service import BudgetService
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import suggest_category


# ---------------------------------------------------------------------------
# CategoryService
# ---------------------------------------------------------------------------

class TestCategoryService:
    def test_create_and_retrieve(self, db, app):
        with app.app_context():
            cat = CategoryService.create(name="Rent", icon="🏠", color="#8b5cf6")
            assert cat.id is not None
            fetched = CategoryService.get_by_id(cat.id)
            assert fetched.name == "Rent"

    def test_get_all_returns_sorted(self, db, app):
        with app.app_context():
            CategoryService.create(name="Zara", icon="👗", color="#f43f5e")
            CategoryService.create(name="Apple", icon="🍎", color="#22c55e")
            cats = CategoryService.get_all()
            names = [c.name for c in cats]
            assert names == sorted(names)

    def test_update_name(self, db, app):
        with app.app_context():
            cat = CategoryService.create(name="Old", icon="?", color="#000000")
            updated = CategoryService.update(cat.id, {"name": "New"})
            assert updated.name == "New"

    def test_delete(self, db, app):
        with app.app_context():
            cat = CategoryService.create(name="ToDelete", icon="🗑", color="#ef4444")
            cat_id = cat.id
            CategoryService.delete(cat_id)
            with pytest.raises(ValueError):
                CategoryService.get_by_id(cat_id)

    def test_get_nonexistent_raises(self, db, app):
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                CategoryService.get_by_id(9999)


# ---------------------------------------------------------------------------
# TransactionService
# ---------------------------------------------------------------------------

class TestTransactionService:
    def _make_category(self, app, db):
        with app.app_context():
            cat = Category(name="Food", icon="🍔", color="#f97316")
            db.session.add(cat)
            db.session.commit()
            db.session.refresh(cat)
            return cat.id

    def test_create_expense(self, db, app):
        cat_id = self._make_category(app, db)
        with app.app_context():
            t = TransactionService.create(
                amount=50.0,
                type="expense",
                date=datetime.date(2024, 3, 15),
                description="Pizza",
                category_id=cat_id,
            )
            assert t.id is not None
            assert t.type == "expense"
            assert float(t.amount) == 50.0

    def test_create_with_nonexistent_category_raises(self, db, app):
        with app.app_context():
            with pytest.raises(ValueError, match="does not exist"):
                TransactionService.create(
                    amount=10.0,
                    type="expense",
                    date=datetime.date.today(),
                    description="Ghost cat",
                    category_id=9999,
                )

    def test_filter_by_type(self, db, app):
        with app.app_context():
            TransactionService.create(amount=100, type="income", date=datetime.date.today(), description="Salary", category_id=None)
            TransactionService.create(amount=20, type="expense", date=datetime.date.today(), description="Snacks", category_id=None)
            incomes, _ = TransactionService.get_all(type_filter="income")
            assert all(t.type == "income" for t in incomes)

    def test_delete(self, db, app):
        with app.app_context():
            t = TransactionService.create(amount=5, type="expense", date=datetime.date.today(), description="Coffee", category_id=None)
            t_id = t.id
            TransactionService.delete(t_id)
            with pytest.raises(ValueError):
                TransactionService.get_by_id(t_id)

    def test_update_amount(self, db, app):
        with app.app_context():
            t = TransactionService.create(amount=10, type="expense", date=datetime.date.today(), description="Test", category_id=None)
            updated = TransactionService.update(t.id, {"amount": 99})
            assert float(updated.amount) == 99


# ---------------------------------------------------------------------------
# BudgetService
# ---------------------------------------------------------------------------

class TestBudgetService:
    def _make_category(self, app, db, name="Housing"):
        with app.app_context():
            cat = Category(name=name, icon="🏠", color="#8b5cf6")
            db.session.add(cat)
            db.session.commit()
            db.session.refresh(cat)
            return cat.id

    def test_create_budget(self, db, app):
        cat_id = self._make_category(app, db)
        with app.app_context():
            b = BudgetService.create(category_id=cat_id, month="2024-03", limit_amount=1500)
            assert b.id is not None
            assert b.month == "2024-03"

    def test_duplicate_budget_raises_integrity_error(self, db, app):
        """DB-level unique constraint prevents duplicate budgets for same cat+month."""
        from sqlalchemy.exc import IntegrityError
        cat_id = self._make_category(app, db, name="Unique")
        with app.app_context():
            BudgetService.create(category_id=cat_id, month="2024-03", limit_amount=500)
            with pytest.raises(IntegrityError):
                BudgetService.create(category_id=cat_id, month="2024-03", limit_amount=600)

    def test_actuals_computation(self, db, app):
        cat_id = self._make_category(app, db, name="Food")
        with app.app_context():
            BudgetService.create(category_id=cat_id, month="2024-03", limit_amount=300)
            # Add two expenses for that month
            TransactionService = __import__("app.services.transaction_service", fromlist=["TransactionService"]).TransactionService
            TransactionService.create(amount=80, type="expense", date=datetime.date(2024, 3, 10), description="Shop", category_id=cat_id)
            TransactionService.create(amount=50, type="expense", date=datetime.date(2024, 3, 20), description="Dinner", category_id=cat_id)
            result = BudgetService.get_with_actuals("2024-03")
            assert len(result) == 1
            assert result[0]["spent"] == 130.0
            assert result[0]["remaining"] == 170.0


# ---------------------------------------------------------------------------
# AnalyticsService
# ---------------------------------------------------------------------------

class TestAnalyticsService:
    def test_monthly_summary_empty(self, db, app):
        with app.app_context():
            summary = AnalyticsService.monthly_summary("2020-01")
            assert summary["income"] == 0.0
            assert summary["expense"] == 0.0
            assert summary["net"] == 0.0

    def test_monthly_summary_with_data(self, db, app):
        with app.app_context():
            from app.services.transaction_service import TransactionService
            TransactionService.create(amount=3000, type="income", date=datetime.date(2024, 3, 1), description="Salary", category_id=None)
            TransactionService.create(amount=200, type="expense", date=datetime.date(2024, 3, 5), description="Bills", category_id=None)
            summary = AnalyticsService.monthly_summary("2024-03")
            assert summary["income"] == 3000.0
            assert summary["expense"] == 200.0
            assert summary["net"] == 2800.0


# ---------------------------------------------------------------------------
# AiService (unit — no DB)
# ---------------------------------------------------------------------------

class TestAiService:
    def test_grocery_match(self):
        result = suggest_category("Weekly Walmart groceries run")
        assert result["category"] == "Groceries"
        assert result["confidence"] == 1.0

    def test_restaurant_match(self):
        result = suggest_category("Lunch at McDonald's")
        assert result["category"] == "Dining"

    def test_salary_match(self):
        result = suggest_category("Monthly salary deposit")
        assert result["category"] == "Income"

    def test_netflix_match(self):
        result = suggest_category("Netflix subscription renewal")
        assert result["category"] in ("Entertainment", "Subscriptions")

    def test_no_match_returns_other(self):
        result = suggest_category("xkcd1234randomnonsense")
        assert result["category"] == "Other"
        assert result["confidence"] == 0.0

    def test_case_insensitive(self):
        result = suggest_category("STARBUCKS COFFEE")
        assert result["category"] == "Dining"
