from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.core.database import get_db
from app.models.brand import VehicleBrand
from app.models.model import VehicleModel
from app.models.color import Color
from app.models.formula import Formula
from app.models.user import User
from app.schemas.color import ColorCreate, ColorUpdate, ColorOut
from app.auth.deps import get_current_active_admin
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/search", response_model=List[ColorOut])
def search_colors(
    code: Optional[str] = None,
    name: Optional[str] = None,
    brand_id: Optional[int] = None,
    model_id: Optional[int] = None,
    paint_system: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Search colors by code, name, brand, or model"""
    query = (
        db.query(Color)
        .options(joinedload(Color.brand), joinedload(Color.model), joinedload(Color.formulas))
        .filter(Color.is_active == True)
    )

    if code:
        clean_code = f"%{code.strip().lower()}%"
        query = query.filter(func.lower(Color.color_code).like(clean_code))
    if name:
        clean_name = f"%{name.strip().lower()}%"
        query = query.filter(func.lower(Color.color_name).like(clean_name))
    if brand_id:
        query = query.filter(Color.brand_id == brand_id)
    if model_id:
        query = query.filter(Color.model_id == model_id)
    if paint_system:
        query = query.filter(Color.paint_system == paint_system)

    colors = query.order_by(Color.color_code.asc()).offset(skip).limit(limit).all()

    result = []
    for c in colors:
        out = ColorOut.model_validate(c)
        out.brand_name = c.brand.name if c.brand else None
        out.model_name = c.model.name if c.model else None
        out.formulas_count = len(c.formulas)
        result.append(out)
    return result


@router.get("/{color_id}", response_model=ColorOut)
def get_color(color_id: int, db: Session = Depends(get_db)):
    c = (
        db.query(Color)
        .options(joinedload(Color.brand), joinedload(Color.model), joinedload(Color.formulas))
        .filter(Color.id == color_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Color not found.")
    out = ColorOut.model_validate(c)
    out.brand_name = c.brand.name if c.brand else None
    out.model_name = c.model.name if c.model else None
    out.formulas_count = len(c.formulas)
    return out


@router.get("/admin/all", response_model=List[ColorOut])
def get_admin_colors(
    brand_id: Optional[int] = None,
    query_text: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: list all colors"""
    query = db.query(Color).options(joinedload(Color.brand), joinedload(Color.model), joinedload(Color.formulas))
    if brand_id:
        query = query.filter(Color.brand_id == brand_id)
    if query_text:
        term = f"%{query_text.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Color.color_code).like(term),
                func.lower(Color.color_name).like(term),
            )
        )

    colors = query.order_by(Color.color_code.asc()).offset(skip).limit(limit).all()
    result = []
    for c in colors:
        out = ColorOut.model_validate(c)
        out.brand_name = c.brand.name if c.brand else None
        out.model_name = c.model.name if c.model else None
        out.formulas_count = len(c.formulas)
        result.append(out)
    return result


@router.post("/admin", response_model=ColorOut, status_code=status.HTTP_201_CREATED)
def create_color(
    color_in: ColorCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: create new Color"""
    brand = db.query(VehicleBrand).filter(VehicleBrand.id == color_in.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found.")

    if color_in.model_id:
        model = db.query(VehicleModel).filter(VehicleModel.id == color_in.model_id).first()
        if not model or model.brand_id != brand.id:
            raise HTTPException(status_code=400, detail="Invalid model for selected brand.")

    # Check composite uniqueness: (brand_id, color_code, paint_system)
    duplicate = (
        db.query(Color)
        .filter(
            Color.brand_id == color_in.brand_id,
            Color.color_code.ilike(color_in.color_code),
            Color.paint_system.ilike(color_in.paint_system),
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail=f"Color code '{color_in.color_code}' for brand '{brand.name}' with system '{color_in.paint_system}' already exists.",
        )

    color = Color(
        brand_id=color_in.brand_id,
        model_id=color_in.model_id,
        color_code=color_in.color_code.strip(),
        color_name=color_in.color_name.strip(),
        color_type=color_in.color_type,
        paint_system=color_in.paint_system.strip(),
        notes=color_in.notes,
        is_active=color_in.is_active,
    )
    db.add(color)
    db.commit()
    db.refresh(color)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="CREATE",
        entity="Color",
        entity_id=color.id,
        new_value={"code": color.color_code, "name": color.color_name, "brand": brand.name},
        details=f"Created color {color.color_code} {color.color_name}",
    )

    out = ColorOut.model_validate(color)
    out.brand_name = brand.name
    return out


@router.put("/admin/{color_id}", response_model=ColorOut)
def update_color(
    color_id: int,
    color_in: ColorUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: update Color"""
    color = (
        db.query(Color)
        .options(joinedload(Color.brand), joinedload(Color.model), joinedload(Color.formulas))
        .filter(Color.id == color_id)
        .first()
    )
    if not color:
        raise HTTPException(status_code=404, detail="Color not found.")

    if color_in.color_code is not None:
        color.color_code = color_in.color_code.strip()
    if color_in.color_name is not None:
        color.color_name = color_in.color_name.strip()
    if color_in.color_type is not None:
        color.color_type = color_in.color_type
    if color_in.paint_system is not None:
        color.paint_system = color_in.paint_system.strip()
    if color_in.notes is not None:
        color.notes = color_in.notes
    if color_in.is_active is not None:
        color.is_active = color_in.is_active

    brand_id = color_in.brand_id if color_in.brand_id is not None else color.brand_id
    model_id = color_in.model_id if "model_id" in color_in.model_fields_set else color.model_id
    brand = db.query(VehicleBrand).filter(VehicleBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found.")
    if model_id is not None:
        model = db.query(VehicleModel).filter(VehicleModel.id == model_id).first()
        if not model or model.brand_id != brand_id:
            raise HTTPException(status_code=400, detail="Invalid model for selected brand.")
    color.brand_id = brand_id
    if "model_id" in color_in.model_fields_set:
        color.model_id = model_id

    db.commit()
    db.refresh(color)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="UPDATE",
        entity="Color",
        entity_id=color.id,
        details=f"Updated color {color.color_code} {color.color_name}",
    )

    out = ColorOut.model_validate(color)
    out.brand_name = color.brand.name if color.brand else None
    out.model_name = color.model.name if color.model else None
    out.formulas_count = len(color.formulas)
    return out
