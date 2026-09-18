from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; email: EmailStr; role: str
class Token(BaseModel):
    access_token: str; token_type: str = "bearer"
class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    marketplace: str; price: float; discount_pct: float; recorded_at: datetime
class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; name: str; brand: str; category: str; description: str; image_url: str; rating: float; stock: int; prices: list[PriceOut] = []
class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    marketplace: str; price: float; recorded_at: datetime
class AlertCreate(BaseModel):
    product_id: int
    min_price: float = Field(gt=0)
    max_price: float = Field(gt=0)
    # Backward-compatible field for older clients. The new UI sends a range.
    target_price: float | None = Field(default=None, gt=0)
class CartAdd(BaseModel):
    product_id: int; quantity: int = Field(default=1, ge=1, le=20)
class CartUpdate(BaseModel):
    quantity: int = Field(ge=1, le=20)
class CheckoutOut(BaseModel):
    id: int; status: str; total: float; created_at: datetime
