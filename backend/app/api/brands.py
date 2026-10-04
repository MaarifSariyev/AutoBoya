from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.brand import VehicleBrand
from app.models.user import User
from app.schemas.brand import VehicleBrandCreate, VehicleBrandUpdate, VehicleBrandOut
from app.auth.deps import get_current_active_admin
from app.services.audit_service import AuditService

router = APIRouter()


# Public endpoints
@router.get("", response_model=List[VehicleBrandOut])
def get_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Public: list active vehicle brands"""
    return (
        db.query(VehicleBrand)
        .filter(VehicleBrand.is_active == True)
        .order_by(VehicleBrand.name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# Admin endpoints
@router.get("/admin", response_model=List[VehicleBrandOut])
def get_admin_brands(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: list all vehicle brands (including inactive)"""
    return db.query(VehicleBrand).order_by(VehicleBrand.name.asc()).offset(skip).limit(limit).all()


@router.post("/admin", response_model=VehicleBrandOut, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: VehicleBrandCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: create new vehicle brand"""
    existing = db.query(VehicleBrand).filter(VehicleBrand.name.ilike(brand_in.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Brand '{brand_in.name}' already exists.")

    slug = brand_in.slug or brand_in.name.lower().strip().replace(" ", "-").replace("/", "-")
    brand = VehicleBrand(
        name=brand_in.name.strip(),
        slug=slug,
        country=brand_in.country,
        is_active=brand_in.is_active,
    )
    db.add(brand)
    db.commit()
    db.refresh(brand)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="CREATE",
        entity="Brand",
        entity_id=brand.id,
        new_value={"name": brand.name, "country": brand.country},
        details=f"Created brand {brand.name}",
    )

    return brand


@router.put("/admin/{brand_id}", response_model=VehicleBrandOut)
def update_brand(
    brand_id: int,
    brand_in: VehicleBrandUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: update brand"""
    brand = db.query(VehicleBrand).filter(VehicleBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    old_val = {"name": brand.name, "is_active": brand.is_active}
    if brand_in.name is not None:
        brand.name = brand_in.name.strip()
    if brand_in.slug is not None:
        brand.slug = brand_in.slug.strip()
    if brand_in.country is not None:
        brand.country = brand_in.country.strip()
    if brand_in.is_active is not None:
        brand.is_active = brand_in.is_active

    db.commit()
    db.refresh(brand)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="UPDATE",
        entity="Brand",
        entity_id=brand.id,
        old_value=old_val,
        new_value={"name": brand.name, "is_active": brand.is_active},
        details=f"Updated brand {brand.name}",
    )

    return brand
