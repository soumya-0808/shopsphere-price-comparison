"""Background demo market updater.

This simulates permitted retailer-feed updates for the portfolio build. It does
not scrape retailer websites. Production should replace this with authorized
affiliate/API/feed data and exact SKU matching.
"""
import time
from datetime import datetime, timezone, timedelta
from random import Random
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import Base, engine, SessionLocal
from app.models import Product, ProductPrice, PriceHistory

rng = Random(20260918)
MARKET_LIMIT = 0.018

def update_once(write_history: bool = False):
    db = SessionLocal()
    try:
        products = db.scalars(select(Product).options(selectinload(Product.prices))).all()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for product in products:
            for offer in product.prices:
                # Small independent movement: most ticks are tiny, occasional
                # promotional movement is larger. Prices stay positive.
                step = rng.uniform(-0.006, 0.006)
                if rng.random() < 0.035:
                    step += rng.choice([-1, 1]) * rng.uniform(0.008, 0.016)
                offer.price = round(max(100, offer.price * (1 + step)) / 10) * 10
                offer.recorded_at = now
                if rng.random() < 0.08:
                    offer.discount_pct = round(max(2, min(22, offer.discount_pct + rng.uniform(-1.0, 1.0))), 1)
                if write_history:
                    db.add(PriceHistory(product_id=product.id, marketplace=offer.marketplace,
                                         price=float(offer.price), recorded_at=now))
        if write_history:
            cutoff = now - timedelta(days=45)
            db.query(PriceHistory).filter(PriceHistory.recorded_at < cutoff).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

def main():
    Base.metadata.create_all(engine)
    tick = 0
    while True:
        try:
            update_once(write_history=(tick % 10 == 0))
        except Exception as exc:
            print(f"market updater: {exc}", flush=True)
        tick += 1
        time.sleep(60)

if __name__ == "__main__":
    main()
