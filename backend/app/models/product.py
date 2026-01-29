"""Product and ProductImage models."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    min_order_quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(50), default="piece")
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", back_populates="products", lazy="selectin")
    category = relationship("Category", back_populates="products", lazy="selectin")
    images = relationship("ProductImage", back_populates="product", lazy="selectin", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product", lazy="selectin")



class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alt: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product = relationship("Product", back_populates="images", lazy="selectin")
