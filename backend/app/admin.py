"""
Django-style admin UI for inspecting and editing data.
Visit /admin when the app is running (protect in production with auth).
"""
from sqlalchemy import create_engine
from sqladmin import Admin, ModelView

from app.config import get_settings
from app.models.user import User
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.conversation import Conversation, Message
from app.models.presence import UserPresence


def get_sync_engine():
    """Sync engine for SQLAdmin (admin UI uses sync SQLAlchemy)."""
    settings = get_settings()
    url = settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return create_engine(url, pool_pre_ping=True)


def setup_admin(app):
    """Mount SQLAdmin on the FastAPI app. Call from main.py."""
    engine = get_sync_engine()
    admin = Admin(app, engine, title="Marketplace Admin", base_url="/admin")

    class UserAdmin(ModelView, model=User):
        name = "User"
        name_plural = "Users"
        icon = "fa-solid fa-user"
        column_list = [User.id, User.email, User.full_name, User.role, User.is_active, User.created_at]
        column_searchable_list = [User.email, User.full_name]
        column_sortable_list = [User.id, User.email, User.created_at]
        column_default_sort = [(User.created_at, True)]

    class CategoryAdmin(ModelView, model=Category):
        name = "Category"
        name_plural = "Categories"
        icon = "fa-solid fa-folder"
        column_list = [Category.id, Category.name, Category.slug, Category.sort_order]

    class ProductImageAdmin(ModelView, model=ProductImage):
        name = "Product Image"
        name_plural = "Product Images"
        column_list = [ProductImage.id, ProductImage.product_id, ProductImage.url, ProductImage.sort_order]

    class ProductAdmin(ModelView, model=Product):
        name = "Product"
        name_plural = "Products"
        icon = "fa-solid fa-box"
        column_list = [
            Product.id,
            Product.title,
            Product.slug,
            Product.price,
            Product.seller_id,
            Product.category_id,
            Product.is_active,
            Product.created_at,
        ]
        column_searchable_list = [Product.title]
        column_sortable_list = [Product.id, Product.price, Product.created_at]
        column_default_sort = [(Product.created_at, True)]

    class OrderItemAdmin(ModelView, model=OrderItem):
        name = "Order Item"
        name_plural = "Order Items"
        column_list = [OrderItem.id, OrderItem.order_id, OrderItem.product_id, OrderItem.quantity, OrderItem.unit_price, OrderItem.subtotal]

    class OrderAdmin(ModelView, model=Order):
        name = "Order"
        name_plural = "Orders"
        icon = "fa-solid fa-shopping-cart"
        column_list = [
            Order.id,
            Order.buyer_id,
            Order.status,
            Order.total_amount,
            Order.shipping_address,
            Order.created_at,
        ]
        column_sortable_list = [Order.id, Order.created_at]
        column_default_sort = [(Order.created_at, True)]

    class CartItemAdmin(ModelView, model=CartItem):
        name = "Cart Item"
        name_plural = "Cart Items"
        column_list = [CartItem.id, CartItem.user_id, CartItem.product_id, CartItem.quantity]

    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(CartItemAdmin)

    class MessageAdmin(ModelView, model=Message):
        name = "Message"
        name_plural = "Messages"
        column_list = [Message.id, Message.conversation_id, Message.sender_id, Message.body, Message.is_read, Message.created_at]

    class ConversationAdmin(ModelView, model=Conversation):
        name = "Conversation"
        name_plural = "Conversations"
        icon = "fa-solid fa-comments"
        column_list = [Conversation.id, Conversation.buyer_id, Conversation.seller_id, Conversation.product_id, Conversation.created_at]

    admin.add_view(ConversationAdmin)
    admin.add_view(MessageAdmin)

    class UserPresenceAdmin(ModelView, model=UserPresence):
        name = "Presence"
        name_plural = "Presence"
        column_list = [UserPresence.user_id, UserPresence.last_seen_at]

    admin.add_view(UserPresenceAdmin)
