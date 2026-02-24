"""BudgetService — CRUD and budget-vs-actuals computation."""
from decimal import Decimal
from typing import Optional

import structlog
from sqlalchemy import func, String

from app.database import db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.category import Category

log = structlog.get_logger()


class BudgetService:

    @staticmethod
    def get_all(month: Optional[str] = None) -> list[Budget]:
        q = Budget.query
        if month:
            q = q.filter(Budget.month == month)
        return q.order_by(Budget.month.desc()).all()

    @staticmethod
    def get_by_id(budget_id: int) -> Budget:
        b = db.session.get(Budget, budget_id)
        if b is None:
            raise ValueError(f"Budget {budget_id} not found")
        return b

    @staticmethod
    def create(*, category_id: int, month: str, limit_amount: Decimal) -> Budget:
        cat = db.session.get(Category, category_id)
        if cat is None:
            raise ValueError(f"Category {category_id} does not exist")
        b = Budget(category_id=category_id, month=month, limit_amount=limit_amount)
        db.session.add(b)
        db.session.commit()
        log.info("budget_created", id=b.id, category_id=category_id, month=month)
        return b

    @staticmethod
    def update(budget_id: int, data: dict) -> Budget:
        b = BudgetService.get_by_id(budget_id)
        if "category_id" in data:
            cat = db.session.get(Category, data["category_id"])
            if cat is None:
                raise ValueError(f"Category {data['category_id']} does not exist")
        for field, value in data.items():
            setattr(b, field, value)
        db.session.commit()
        log.info("budget_updated", id=b.id)
        return b

    @staticmethod
    def delete(budget_id: int) -> None:
        b = BudgetService.get_by_id(budget_id)
        db.session.delete(b)
        db.session.commit()
        log.info("budget_deleted", id=budget_id)

    @staticmethod
    def get_with_actuals(month: str) -> list[dict]:
        """
        Return each budget for *month* augmented with the total spent so far.

        The spent amount is computed in a single aggregation query so we
        don't issue N+1 queries as the number of budgets grows.
        """
        budgets = BudgetService.get_all(month=month)
        if not budgets:
            return []

        # Aggregate expenses grouped by category for the month ---
        # We filter transactions whose date starts with 'YYYY-MM'
        spent_rows = (
            db.session.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label("spent"),
            )
            .filter(
                Transaction.type == "expense",
                func.substr(func.cast(Transaction.date, String), 1, 7) == month,
            )
            .group_by(Transaction.category_id)
            .all()
        )
        spent_map: dict[int, float] = {
            row.category_id: float(row.spent) for row in spent_rows
        }

        result = []
        for b in budgets:
            spent = spent_map.get(b.category_id, 0.0)
            d = b.to_dict()
            d["spent"] = spent
            d["remaining"] = round(float(b.limit_amount) - spent, 2)
            d["utilization_pct"] = (
                round(spent / float(b.limit_amount) * 100, 1)
                if float(b.limit_amount) > 0
                else 0.0
            )
            result.append(d)
        return result
