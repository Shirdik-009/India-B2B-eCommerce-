# Code quality & optimization

## Structure

- **Layered**: `api/` (HTTP), `core/` (auth, deps), `models/`, `schemas/`, `admin/`. No business logic in `main.py`.
- **Single responsibility**: Routers by domain (auth, products, orders, chat, cart). Shared logic in `core/` and helpers (e.g. `_conversation_response` in chat).
- **DRY**: Response builders reused where it makes sense; Pydantic schemas for validation and serialization.

## Database

- **Async**: SQLAlchemy async engine + asyncpg; one `get_db()` dependency for request-scoped sessions.
- **No N+1**: List endpoints use `selectinload()` for related data (e.g. Order + items + product, Conversation + buyer/seller/product). Chat inbox uses a subquery for “latest message per conversation” instead of loading all messages.
- **Pagination**: List endpoints accept `page` and `page_size`; counts use `func.count()` in a separate query where needed.
- **Indexes**: Unique and FKs where appropriate (e.g. `uq_conversation_buyer_seller`).

## Security

- **Auth**: JWT in `core/security.py`; `get_current_user` / `get_current_user_seller` in `core/deps.py`. No auth logic in route handlers.
- **Input**: Pydantic schemas with `Field(..., min_length=..., max_length=...)` and validators. Role checks before seller-only actions.

## What to watch as you grow

- **Services layer**: If route handlers get fat, move business logic into `app/services/` and keep routes thin.
- **Caching**: Add Redis for hot reads (e.g. product list, categories) when needed.
- **Migrations**: Use Alembic for schema changes; avoid `create_all` in production.
