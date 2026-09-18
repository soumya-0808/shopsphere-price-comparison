from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import Base, engine
from app.api import auth, products, user
from sqlalchemy import text, select
from app.models import Product, ProductPrice

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    # Keep existing local PostgreSQL volumes compatible with the current alert model.
    ensure_price_alert_columns()
    ensure_marketplace_demo_prices()
    yield


def ensure_price_alert_columns():
    """Safely migrate old local PostgreSQL volumes to the current alert schema."""
    from sqlalchemy import text
    statements = [
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS target_price DOUBLE PRECISION",
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS min_price DOUBLE PRECISION",
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS max_price DOUBLE PRECISION",
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS last_notified_at TIMESTAMP",
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE",
        "ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "CREATE INDEX IF NOT EXISTS ix_products_category_lower ON products (lower(category))",
        "CREATE INDEX IF NOT EXISTS ix_products_brand_lower ON products (lower(brand))",
        "CREATE INDEX IF NOT EXISTS ix_product_prices_product_id ON product_prices (product_id)",
        "CREATE INDEX IF NOT EXISTS ix_price_history_product_recorded ON price_history (product_id, recorded_at)",
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
        conn.execute(text(
            "UPDATE price_alerts SET min_price = target_price WHERE min_price IS NULL AND target_price IS NOT NULL"
        ))
        conn.execute(text(
            "UPDATE price_alerts SET max_price = target_price WHERE max_price IS NULL AND target_price IS NOT NULL"
        ))
        conn.execute(text(
            "UPDATE price_alerts SET active = TRUE WHERE active IS NULL"
        ))
        conn.execute(text(
            "UPDATE price_alerts SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"
        ))


app = FastAPI(title=settings.app_name, version="1.0.0", description="ShopSphere AI-powered e-commerce and price intelligence API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(user.router, prefix="/api")

@app.get("/api/health")
def health(): return {"status":"ok","service":"shopsphere-api"}


def ensure_marketplace_demo_prices():
    """Repair legacy local data so the demo genuinely compares different retailers.

    Older ShopSphere databases could have been seeded with Amazon as the cheapest
    offer for nearly every product. The current demo intentionally rotates the
    cheapest retailer across the catalog. If the existing database still has the
    old pattern, reseed the reference offers automatically once at API startup.
    """
    try:
        from app.services.seed import seed, PRODUCTS
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            product_count = db.query(Product).count()
            if product_count < len(PRODUCTS):
                needs_repair = True
            else:
                rows = db.execute(
                    select(ProductPrice.product_id, ProductPrice.marketplace, ProductPrice.price)
                    .order_by(ProductPrice.product_id)
                ).all()
                by_product = {}
                for product_id, marketplace, price in rows:
                    by_product.setdefault(product_id, []).append((marketplace, float(price)))
                amazon_low = 0
                comparable = 0
                for offers in by_product.values():
                    if len(offers) < 3:
                        continue
                    comparable += 1
                    if min(offers, key=lambda x: x[1])[0] == "Amazon":
                        amazon_low += 1
                needs_repair = comparable == 0 or amazon_low / comparable > 0.65
        finally:
            db.close()
        if needs_repair:
            seed()
    except Exception as exc:
        # Startup should remain available even if a local demo-data repair fails.
        print(f"marketplace demo-data repair skipped: {exc}", flush=True)
