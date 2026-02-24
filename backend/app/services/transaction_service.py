"""
TransactionService — all business logic for transactions.

Design decisions:
- Takes `db.session` as a dependency (passed in by routes), making it
  easy to inject a test session without monkeypatching globals.
- Returns domain objects (ORM instances), not dicts — serialisation is
  the route's responsibility.
- Raises ValueError for "business rule" violations (e.g. category not
  found) so callers don't need to know about SQLAlchemy internals.
"""
import datetime
from decimal import Decimal
from typing import Optional

import structlog

from app.database import db
from app.models.transaction import Transaction
from app.models.category import Category

log = structlog.get_logger()


class TransactionService:

    @staticmethod
    def get_all(
        *,
        type_filter: Optional[str] = None,
        category_id: Optional[int] = None,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Transaction], int]:
        """Return (records, total_count) with optional filters."""
        q = Transaction.query
        if type_filter:
            q = q.filter(Transaction.type == type_filter)
        if category_id is not None:
            q = q.filter(Transaction.category_id == category_id)
        if date_from:
            q = q.filter(Transaction.date >= date_from)
        if date_to:
            q = q.filter(Transaction.date <= date_to)
        total = q.count()
        records = q.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
        return records, total

    @staticmethod
    def get_by_id(transaction_id: int) -> Transaction:
        t = db.session.get(Transaction, transaction_id)
        if t is None:
            raise ValueError(f"Transaction {transaction_id} not found")
        return t

    @staticmethod
    def create(
        *,
        amount: Decimal,
        type: str,
        date: datetime.date,
        description: str,
        category_id: Optional[int],
    ) -> Transaction:
        if category_id is not None:
            cat = db.session.get(Category, category_id)
            if cat is None:
                raise ValueError(f"Category {category_id} does not exist")
        t = Transaction(
            amount=amount,
            type=type,
            date=date,
            description=description,
            category_id=category_id,
        )
        db.session.add(t)
        db.session.commit()
        log.info("transaction_created", id=t.id, type=type, amount=str(amount))
        return t

    @staticmethod
    def update(transaction_id: int, data: dict) -> Transaction:
        t = TransactionService.get_by_id(transaction_id)
        if "category_id" in data and data["category_id"] is not None:
            cat = db.session.get(Category, data["category_id"])
            if cat is None:
                raise ValueError(f"Category {data['category_id']} does not exist")
        for field, value in data.items():
            setattr(t, field, value)
        db.session.commit()
        log.info("transaction_updated", id=t.id)
        return t

    @staticmethod
    def delete(transaction_id: int) -> None:
        t = TransactionService.get_by_id(transaction_id)
        db.session.delete(t)
        db.session.commit()
        log.info("transaction_deleted", id=transaction_id)
