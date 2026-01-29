"""Category model for product taxonomy."""
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent = relationship("Category", remote_side="Category.id", backref="children")
    products = relationship("Product", back_populates="category", lazy="selectin")
