"""Category model.

A category groups transactions (e.g. 'Groceries', 'Rent', 'Salary').
It is intentionally simple: name uniqueness is enforced at the DB level so
duplicate categories are impossible regardless of which code path creates them.
"""
import re

from app.database import db


_NAME_CLEAN_RE = re.compile(r"[^\w\s&-]+")


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    icon = db.Column(db.String(8), nullable=False, default="💰")
    color = db.Column(db.String(7), nullable=False, default="#6366f1")  # hex

    # Relationship — used for budget lookups, not lazy-loaded in list endpoints
    transactions = db.relationship(
        "Transaction", back_populates="category", lazy="dynamic"
    )
    budgets = db.relationship(
        "Budget", back_populates="category", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"

    def to_dict(self) -> dict:
        # Clean name for UI so fonts that do not support emoji or
        # special symbols do not render replacement question marks.
        clean_name = _NAME_CLEAN_RE.sub("", self.name or "").strip() or self.name
        return {
            "id": self.id,
            "name": clean_name,
            "icon": self.icon,
            "color": self.color,
        }
