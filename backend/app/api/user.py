from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload
from app.core.security import current_user
from app.db.session import get_db
from app.models import Product, Wishlist, PriceAlert, User
from app.schemas.schemas import AlertCreate, ProductOut

router = APIRouter(prefix="/me", tags=["User"])

def with_prices(db, ids):
    return db.scalars(select(Product).options(selectinload(Product.prices)).where(Product.id.in_(ids))).all() if ids else []

@router.get("/wishlist", response_model=list[ProductOut])
def wishlist(user: User = Depends(current_user), db: Session = Depends(get_db)):
    ids = db.scalars(select(Wishlist.product_id).where(Wishlist.user_id == user.id)).all()
    return with_prices(db, ids)

@router.post("/wishlist/{product_id}")
def add_wishlist(product_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not db.get(Product, product_id): raise HTTPException(404, "Product not found")
    existing = db.scalar(select(Wishlist).where(Wishlist.user_id == user.id, Wishlist.product_id == product_id))
    if not existing:
        db.add(Wishlist(user_id=user.id, product_id=product_id)); db.commit()
    return {"message": "Added to wishlist"}

@router.delete("/wishlist/{product_id}")
def remove_wishlist(product_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(Wishlist).where(Wishlist.user_id == user.id, Wishlist.product_id == product_id))
    if row: db.delete(row); db.commit()
    return {"message": "Removed"}

@router.post("/price-alerts")
def price_alert(data: AlertCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    lo = float(data.min_price)
    hi = float(data.max_price)
    if lo <= 0 or hi <= 0:
        raise HTTPException(422, "Prices must be greater than zero")
    if hi < lo:
        raise HTTPException(422, "Maximum price must be greater than or equal to minimum price")

    # Keep one active alert per product for a predictable user experience.
    try:
        old = db.scalars(select(PriceAlert).where(
            PriceAlert.user_id == user.id,
            PriceAlert.product_id == data.product_id,
            PriceAlert.active.is_(True)
        )).all()
        for item in old:
            item.active = False

        row = PriceAlert(
            user_id=user.id, product_id=data.product_id, target_price=lo,
            min_price=lo, max_price=hi, active=True
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(500, "The price-alert database is not ready. Restart the API container once and try again.") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(500, "Could not save the price alert. Please try again.") from exc

    return {"id": row.id, "message": "Price alert created", "min_price": row.min_price, "max_price": row.max_price}

@router.get("/price-alerts")
def list_price_alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(PriceAlert).where(PriceAlert.user_id == user.id).order_by(PriceAlert.created_at.desc())).all()
    out = []
    for row in rows:
        p = db.scalar(select(Product).options(selectinload(Product.prices)).where(Product.id == row.product_id))
        if not p: continue
        current = min((x.price for x in p.prices), default=None)
        out.append({"id": row.id, "product_id": row.product_id, "product_name": p.name, "brand": p.brand,
                    "image_url": p.image_url, "min_price": row.min_price or row.target_price,
                    "max_price": row.max_price or row.target_price, "current_price": current,
                    "active": row.active, "triggered": row.last_notified_at is not None,
                    "in_range_now": current is not None and (row.min_price or row.target_price) <= current <= (row.max_price or row.target_price),
                    "created_at": row.created_at})
    return out

@router.post("/price-alerts/{alert_id}/seen")
def mark_alert_seen(alert_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(PriceAlert).where(PriceAlert.id == alert_id, PriceAlert.user_id == user.id))
    if not row: raise HTTPException(404, "Alert not found")
    row.last_notified_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return {"message": "Notification recorded"}

@router.delete("/price-alerts/{alert_id}")
def delete_price_alert(alert_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(PriceAlert).where(PriceAlert.id == alert_id, PriceAlert.user_id == user.id))
    if not row: raise HTTPException(404, "Alert not found")
    db.delete(row); db.commit()
    return {"message": "Alert deleted"}

@router.get("/price-alerts/check")
def check_price_alerts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(PriceAlert).where(PriceAlert.user_id == user.id, PriceAlert.active == True)).all()
    triggered = []
    for row in rows:
        p = db.scalar(select(Product).options(selectinload(Product.prices)).where(Product.id == row.product_id))
        if not p or not p.prices: continue
        current = min(x.price for x in p.prices)
        low = row.min_price or row.target_price
        high = row.max_price or row.target_price
        # A real alert fires when the price enters the target range, then is
        # marked inactive so it does not spam the user every minute.
        if low <= current <= high and row.last_notified_at is None:
            row.active = False
            row.last_notified_at = datetime.now(timezone.utc).replace(tzinfo=None)
            triggered.append({"id": row.id, "product_id": p.id, "product_name": p.name, "brand": p.brand,
                              "current_price": current, "min_price": low, "max_price": high,
                              "marketplace": min(p.prices, key=lambda x:x.price).marketplace,
                              "triggered_at": row.last_notified_at})
    if triggered:
        db.commit()
    return {"triggered": triggered}

@router.post("/price-alerts/{alert_id}/reactivate")
def reactivate_price_alert(alert_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(PriceAlert).where(PriceAlert.id == alert_id, PriceAlert.user_id == user.id))
    if not row:
        raise HTTPException(404, "Alert not found")
    row.active = True
    row.last_notified_at = None
    db.commit()
    return {"message": "Price alert reactivated", "id": row.id}

@router.get("/recommendations", response_model=list[ProductOut])
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    wish = db.scalars(select(Product).join(Wishlist, Wishlist.product_id == Product.id).where(Wishlist.user_id == user.id)).all()
    if not wish:
        return db.scalars(select(Product).options(selectinload(Product.prices)).order_by(Product.rating.desc()).limit(8)).all()
    cats = {p.category for p in wish}; brands = {p.brand for p in wish}
    stmt = select(Product).options(selectinload(Product.prices)).where(Product.category.in_(cats) | Product.brand.in_(brands)).order_by(Product.rating.desc()).limit(8)
    return db.scalars(stmt).all()
