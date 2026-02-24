"""CategoryService — CRUD for categories."""
import structlog

from app.database import db
from app.models.category import Category

log = structlog.get_logger()


class CategoryService:

    @staticmethod
    def get_all() -> list[Category]:
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get_by_id(category_id: int) -> Category:
        cat = db.session.get(Category, category_id)
        if cat is None:
            raise ValueError(f"Category {category_id} not found")
        return cat

    @staticmethod
    def create(*, name: str, icon: str, color: str) -> Category:
        cat = Category(name=name, icon=icon, color=color)
        db.session.add(cat)
        db.session.commit()
        log.info("category_created", id=cat.id, name=name)
        return cat

    @staticmethod
    def update(category_id: int, data: dict) -> Category:
        cat = CategoryService.get_by_id(category_id)
        for field, value in data.items():
            setattr(cat, field, value)
        db.session.commit()
        log.info("category_updated", id=cat.id)
        return cat

    @staticmethod
    def delete(category_id: int) -> None:
        cat = CategoryService.get_by_id(category_id)
        db.session.delete(cat)
        db.session.commit()
        log.info("category_deleted", id=category_id)
