# Models package — expose all models so `init_db` can import them in one line.
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget

__all__ = ["Category", "Transaction", "Budget"]
