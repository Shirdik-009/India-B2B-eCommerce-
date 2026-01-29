# India B2B Marketplace

A full-stack B2B marketplace (Alibaba-style) for India: wholesale sourcing, supplier discovery, registration, login, product catalog, cart, and orders. Built for speed, security, and future AI integration.

## Tech stack

| Layer   | Technology |
|--------|------------|
| Backend | **FastAPI** (Python 3.12) – async, type-safe, OpenAPI, AI-ready |
| Frontend | **Next.js 14** (React, TypeScript) – App Router, SSR-ready |
| Database | **PostgreSQL 16** (async via SQLAlchemy + asyncpg) |
| Cache   | **Redis 7** (optional, for sessions/cache later) |
| Runtime | **Docker & Docker Compose** |

- **Backend**: Clean module layout (`app/`), JWT auth, role-based access (buyer/seller/admin), pagination, search.
- **Frontend**: Separate `frontend/` app, Tailwind CSS, auth context, responsive UI.
- **Security**: Bcrypt passwords, JWT with configurable expiry, CORS, env-based secrets.

## Project structure

```
.
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/              # Routers: auth, users, categories, products, orders, cart
│   │   ├── core/              # Security, dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Next.js app
│   ├── src/
│   │   ├── app/               # Pages (App Router)
│   │   ├── components/
│   │   └── lib/               # API client, auth
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick start with Docker

1. **Clone and set env**

   ```bash
   cp .env.example .env
   # Edit .env: set SECRET_KEY (min 32 chars) for production
   ```

2. **Run everything**

   ```bash
   docker compose up --build
   ```

   - **Backend API**: http://localhost:8000  
   - **API docs**: http://localhost:8000/docs  
   - **Admin UI** (Django-style): http://localhost:8000/admin — browse/edit users, orders, products  
   - **Frontend**: http://localhost:3000  
   - **PostgreSQL**: localhost:5433 (user: `marketplace`, db: `marketplace`)  
   - **Redis**: localhost:6379  

3. **First run**: DB tables are created on startup via `create_all`. For production, use Alembic migrations.

### Inspecting data and queries

- **Admin UI**: Open http://localhost:8000/admin to browse and edit **Users**, **Orders**, **Products**, **Categories**, **Cart Items** (Django-admin style). No auth by default — restrict `/admin` in production (e.g. reverse proxy or add auth).
- **Log SQL queries**: In `.env` set `DEBUG=true`. The backend will echo every SQL query to the console (see `app/config.py` and `app/database.py`).

## Run without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Set in `.env` (or env vars):

- `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/marketplace`
- `SECRET_KEY=your-secret-key-min-32-chars`

Then:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
```

Set in `.env.local` (or env):

- `NEXT_PUBLIC_API_URL=http://localhost:8000`

Then:

```bash
npm run dev
```

Frontend: http://localhost:3000

## Features

- **Auth**: Register (buyer/seller), login, JWT, profile.
- **Products**: List, search (`q`), filter by category/price, product detail, seller info.
- **Categories**: List categories; create (seller/admin).
- **Cart**: Add/update/remove items, view cart (authenticated).
- **Orders**: Create order from cart, list my orders, order detail.
- **Seller**: “My products” (`/api/products?my=1`), add product, edit (by owner).

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/auth/register` | Register (body: email, password, full_name, role, …) |
| POST   | `/api/auth/login`    | Login (body: email, password) |
| GET    | `/api/users/me`      | Current user (Bearer token) |
| GET    | `/api/categories`    | List categories |
| GET    | `/api/products`      | List products (q, category_id, page, page_size, my=1 for seller) |
| GET    | `/api/products/{id}` | Product detail |
| POST   | `/api/products`      | Create product (seller, Bearer) |
| PATCH  | `/api/products/{id}` | Update product (owner, Bearer) |
| DELETE | `/api/products/{id}` | Delete product (owner, Bearer) |
| GET    | `/api/cart`          | Get cart (Bearer) |
| POST   | `/api/cart`          | Add to cart (Bearer) |
| PATCH  | `/api/cart/{id}`     | Update quantity (Bearer) |
| DELETE | `/api/cart/{id}`     | Remove from cart (Bearer) |
| GET    | `/api/orders`        | My orders (Bearer) |
| POST   | `/api/orders`        | Create order (Bearer) |

## Django vs FastAPI for enterprise

**Is Django fast enough for enterprise?** Yes. Django powers large-scale products (e.g. Instagram, Pinterest). For most B2B workloads, DB and architecture matter more than framework; Django is widely used in production.

| | FastAPI (this project) | Django |
|--|------------------------|--------|
| **Speed** | Async by default; high throughput | Sync by default (async support in 4.1+); still very fast |
| **Admin / inspecting data** | Use **SQLAdmin** (included): http://localhost:8000/admin | Built-in admin and `connection.queries` / Debug Toolbar |
| **Query logging** | Set `DEBUG=true` → SQL echoed to console | `DEBUG=True` + Django Debug Toolbar or `connection.queries` |
| **API style** | Native async, OpenAPI, type hints | Django REST framework (sync unless you add async) |
| **Best for** | High concurrency APIs, microservices, AI pipelines | Full-stack apps, rapid development, built-in admin/auth |

You can keep FastAPI and get Django-like visibility by using the **Admin UI** and **DEBUG** logging above. If you prefer Django’s batteries-included experience (admin, ORM, migrations, auth), you can build the same marketplace in Django; it is enterprise-ready.

## Adding AI later

- Backend is Python/FastAPI: easy to add OpenAI/LangChain endpoints (e.g. product recommendations, search embeddings, chat).
- Keep AI logic in `backend/app/services/` or `backend/app/api/ai.py` and call from existing routes or new ones.

## License

MIT.
