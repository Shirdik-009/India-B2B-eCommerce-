"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base, get_db
from app.api import auth, users, categories, products, orders, cart, chat
from app.admin import setup_admin

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="B2B Marketplace API for India - Alibaba-style platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow localhost origins in dev (any port); use list in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?$" if settings.environment == "development" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# Django-style admin UI: browse/edit users, orders, products at /admin
setup_admin(app)

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
