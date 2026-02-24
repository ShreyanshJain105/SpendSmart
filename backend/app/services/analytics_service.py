"""
AnalyticsService — read-only aggregation queries.

Database compatibility note
----------------------------
SQLite's `strftime('%Y-%m', date)` does NOT work on PostgreSQL (Supabase).
We use `func.substr(func.cast(Transaction.date, String), 1, 7)` instead,
which works on both:
  - SQLite  (stores dates as ISO-8601 text, so cast is a no-op)
  - PostgreSQL / Supabase  (casts DATE → VARCHAR, then slices YYYY-MM)
"""
from sqlalchemy import func, String

from app.database import db
from app.models.transaction import Transaction
from app.models.category import Category


def _month_expr():
    """Cross-db expression that extracts 'YYYY-MM' from a transaction date."""
    return func.substr(func.cast(Transaction.date, String), 1, 7)


class AnalyticsService:

    @staticmethod
    def monthly_summary(month: str) -> dict:
        """Return total income, total expense, and net for *month* (YYYY-MM)."""
        rows = (
            db.session.query(
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(_month_expr() == month)
            .group_by(Transaction.type)
            .all()
        )
        totals = {row.type: float(row.total) for row in rows}
        income = totals.get("income", 0.0)
        expense = totals.get("expense", 0.0)
        return {
            "month": month,
            "income": income,
            "expense": expense,
            "net": round(income - expense, 2),
        }

    @staticmethod
    def category_breakdown(month: str) -> list[dict]:
        """Return expense totals per category for *month*."""
        rows = (
            db.session.query(
                Category.id,
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                Transaction.type == "expense",
                _month_expr() == month,
            )
            .group_by(Category.id)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )
        return [
            {
                "category_id": r.id,
                "category_name": r.name,
                "icon": r.icon,
                "color": r.color,
                "total": float(r.total),
            }
            for r in rows
        ]

    @staticmethod
    def monthly_trends(months: int = 6) -> list[dict]:
        """
        Return income/expense totals for the last *months* calendar months.
        Results are ordered oldest-first (good for charting).
        """
        month_col = _month_expr().label("month")
        rows = (
            db.session.query(
                month_col,
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .group_by(month_col, Transaction.type)
            .order_by(month_col)
            .all()
        )
        # Pivot: month → {income, expense}
        pivot: dict[str, dict] = {}
        for row in rows:
            pivot.setdefault(row.month, {"month": row.month, "income": 0.0, "expense": 0.0})
            pivot[row.month][row.type] = float(row.total)

        # Return only the last N months (sorted)
        sorted_months = sorted(pivot.keys())[-months:]
        return [pivot[m] for m in sorted_months]
