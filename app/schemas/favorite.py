from pydantic import BaseModel
from typing import Optional, List
from .product import ProductInDBBase

class FavoriteToggle(BaseModel):
    product_id: int

class FavoriteResponse(BaseModel):
    id: int
    product_id: int
    product: ProductInDBBase

    class Config:
        from_attributes = True
