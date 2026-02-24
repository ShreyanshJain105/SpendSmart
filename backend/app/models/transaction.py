"""Transaction model.

Design decisions
----------------
* `type` is stored as a plain string with a CHECK constraint ('income' |
  'expense'). Using a Python Enum would require an Alembic migration whenever
  values change; the CHECK constraint fails loudly at the DB level instead.
* `amount` has a CHECK constraint (> 0) so a negative or zero transaction is
  physically impossible — the application cannot accidentally create one.
* `date` stores a Python `date` object (SQLAlchemy maps this to TEXT in SQLite
  with ISO-8601 format, which sorts and filters correctly as strings).
"""
import datetime

from sqlalchemy import CheckConstraint

from app.database import db


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
        CheckConstraint(
            "type IN ('income', 'expense')", name="ck_transaction_type_enum"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    type = db.Column(db.String(8), nullable=False)  # 'income' | 'expense'
    date = db.Column(db.Date, nullable=False, default=datetime.date.today)
    description = db.Column(db.String(256), nullable=False, default="")
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True
    )

    category = db.relationship("Category", back_populates="transactions")

    def __repr__(self) -> str:
        return (
            f"<Transaction id={self.id} type={self.type} amount={self.amount}>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": float(self.amount),
            "type": self.type,
            "date": self.date.isoformat(),
            "description": self.description,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
        }
