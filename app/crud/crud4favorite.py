from sqlalchemy.orm import Session
from app.models.favorite_product import FavoriteProduct
from app.crud import product as product_crud
from app.crud.crud4user_products import check_user_product_access
from fastapi import HTTPException
from typing import Optional

def toggle_favorite(db: Session, product_id: int, tenant_id: int, user_id: Optional[int] = None):
    # 1. Access Check
    has_access = False
    if user_id:
        # Check if User has role-based access to the product
        has_access = check_user_product_access(db, user_id, tenant_id, product_id)
    else:
        # Check if Tenant is subscribed to the product
        has_access = product_crud.get_tenant_product_by_id(db, tenant_id, product_id) is not None

    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied: You cannot favorite a product you aren't assigned to.")

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
