"""Budget model.

A budget sets a spending limit for a category within a calendar month.
The composite unique constraint (category_id, month) ensures you cannot
accidentally have two budgets for the same category+month — a rule that
is enforced at the database level, not just the service layer.
"""
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.database import db


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        CheckConstraint(
            "limit_amount > 0", name="ck_budget_limit_positive"
        ),
        UniqueConstraint("category_id", "month", name="uq_budget_category_month"),
    )

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Stored as 'YYYY-MM' string — simple, sortable, human-readable
    month = db.Column(db.String(7), nullable=False)
    limit_amount = db.Column(db.Numeric(12, 2), nullable=False)

    category = db.relationship("Category", back_populates="budgets")

    def __repr__(self) -> str:
        return (
            f"<Budget id={self.id} category_id={self.category_id} "
            f"month={self.month} limit={self.limit_amount}>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
            "month": self.month,
            "limit_amount": float(self.limit_amount),
        }
