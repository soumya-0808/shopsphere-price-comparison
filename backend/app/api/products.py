from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select, distinct, func, exists
from sqlalchemy.orm import Session, selectinload
from app.db.session import get_db
from app.models import Product, ProductPrice, PriceHistory
from app.schemas.schemas import ProductOut, HistoryOut

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductOut])
def products(q: str | None = None, category: str | None = None, brand: str | None = None,
             min_price: float | None = None, max_price: float | None = None,
             sort: str = "featured", limit: int = Query(48, ge=1, le=100), db: Session = Depends(get_db)):
    # Case-insensitive filters make category/brand navigation reliable even when
    # links use a slightly different capitalization (e.g. Phones vs smartphones).
    stmt = select(Product).options(selectinload(Product.prices))
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(term), Product.brand.ilike(term),
                              Product.category.ilike(term), Product.description.ilike(term)))
    if category and category.strip():
        stmt = stmt.where(func.lower(Product.category) == category.strip().lower())
    if brand and brand.strip():
        stmt = stmt.where(func.lower(Product.brand) == brand.strip().lower())
    # Apply price range before LIMIT so a filtered result cannot become empty
    # simply because matching products occur after the first page.
    if min_price is not None or max_price is not None:
        price_filters = []
        if min_price is not None: price_filters.append(ProductPrice.price >= min_price)
        if max_price is not None: price_filters.append(ProductPrice.price <= max_price)
        stmt = stmt.where(exists(select(ProductPrice.id).where(ProductPrice.product_id == Product.id, *price_filters)))
    if sort == "rating": stmt = stmt.order_by(Product.rating.desc(), Product.id.desc())
    elif sort == "newest": stmt = stmt.order_by(Product.id.desc())
    elif sort == "price_low":
        stmt = stmt.order_by(Product.id.asc())
    else: stmt = stmt.order_by(Product.rating.desc(), Product.id.desc())
    return db.scalars(stmt.limit(limit)).all()

@router.get("/meta/categories")
def categories(db: Session = Depends(get_db)):
    cats = db.scalars(select(distinct(Product.category)).order_by(Product.category)).all()
    brands = db.scalars(select(distinct(Product.brand)).order_by(Product.brand)).all()
    rows = db.execute(select(Product.category, Product.brand).distinct().order_by(Product.category, Product.brand)).all()
    brands_by_category = {}
    for cat, br in rows:
        brands_by_category.setdefault(cat, []).append(br)
    return {"categories": cats, "brands": brands, "brands_by_category": brands_by_category,
            "marketplaces": ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales", "Tata Neu", "Apple Store", "Samsung Shop"]}

@router.get("/{product_id}/history", response_model=list[HistoryOut])
def price_history(product_id: int, marketplace: str | None = None, db: Session = Depends(get_db)):
    if not db.get(Product, product_id): raise HTTPException(404, "Product not found")
    stmt = select(PriceHistory).where(PriceHistory.product_id == product_id).order_by(PriceHistory.recorded_at.asc())
    if marketplace: stmt = stmt.where(PriceHistory.marketplace == marketplace)
    return db.scalars(stmt).all()

@router.get("/{product_id}", response_model=ProductOut)
def product(product_id: int, db: Session = Depends(get_db)):
    p = db.scalar(select(Product).options(selectinload(Product.prices)).where(Product.id == product_id))
    if not p: raise HTTPException(404, "Product not found")
    return p
