from sqlalchemy.orm import Session
from app.models.favorite_product import FavoriteProduct
from app.crud import product as product_crud
from app.crud.crud4user_products import check_user_product_access
from fastapi import HTTPException
from typing import Optional

def toggle_favorite(db: Session, product_id: int, tenant_id: int, user_id: Optional[int] = None):
    # 1. Access Check: Check if Tenant is subscribed to the product.
    # We allow favoriting if the tenant has purchased the product, 
    # even if the specific user doesn't have individual launch access yet.
    has_access = product_crud.get_tenant_product_by_id(db, tenant_id, product_id) is not None

    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You cannot favorite a product that your tenant has not subscribed to."
        )

    # 2. Toggle Logic
    existing = db.query(FavoriteProduct).filter(
        FavoriteProduct.tenant_id == tenant_id,
        FavoriteProduct.user_id == user_id,
        FavoriteProduct.product_id == product_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "removed", "product_id": product_id}
    
    new_fav = FavoriteProduct(
        tenant_id=tenant_id, 
        user_id=user_id, 
        product_id=product_id
    )
    db.add(new_fav)
    db.commit()
    db.refresh(new_fav)
    return {"status": "added", "product_id": product_id}

def get_favorites(db: Session, tenant_id: int, user_id: Optional[int] = None):
    # For a user, we return their personal favorites.
    return db.query(FavoriteProduct).filter(
        FavoriteProduct.tenant_id == tenant_id,
        FavoriteProduct.user_id == user_id
    ).all()
