from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.brand import VehicleBrand
from app.models.model import VehicleModel
from app.models.user import User
from app.schemas.model import VehicleModelCreate, VehicleModelUpdate, VehicleModelOut
from app.auth.deps import get_current_active_admin
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=List[VehicleModelOut])
def get_models(
    brand_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Public: list models, optionally filtered by brand_id"""
    query = (
        db.query(VehicleModel)
        .options(joinedload(VehicleModel.brand))
        .filter(VehicleModel.is_active == True)
    )
    if brand_id:
        query = query.filter(VehicleModel.brand_id == brand_id)
    models = query.order_by(VehicleModel.name.asc()).all()

    # Populate brand_name
    result = []
    for m in models:
        m_out = VehicleModelOut.model_validate(m)
        m_out.brand_name = m.brand.name if m.brand else None
        result.append(m_out)
    return result


@router.get("/admin", response_model=List[VehicleModelOut])
def get_admin_models(
    brand_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: list all models"""
    query = db.query(VehicleModel).options(joinedload(VehicleModel.brand))
    if brand_id:
        query = query.filter(VehicleModel.brand_id == brand_id)
    models = query.order_by(VehicleModel.name.asc()).all()

    result = []
    for m in models:
        m_out = VehicleModelOut.model_validate(m)
        m_out.brand_name = m.brand.name if m.brand else None
        result.append(m_out)
    return result


@router.post("/admin", response_model=VehicleModelOut, status_code=status.HTTP_201_CREATED)
def create_model(
    model_in: VehicleModelCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: create new vehicle model"""
    brand = db.query(VehicleBrand).filter(VehicleBrand.id == model_in.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Vehicle Brand not found")

    existing = (
        db.query(VehicleModel)
        .filter(VehicleModel.brand_id == model_in.brand_id, VehicleModel.name.ilike(model_in.name))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_in.name}' already exists under brand '{brand.name}'.",
        )

    slug = model_in.slug or f"{brand.slug}-{model_in.name.lower().strip().replace(' ', '-')}"
    model = VehicleModel(
        brand_id=model_in.brand_id,
        name=model_in.name.strip(),
        slug=slug,
        year_from=model_in.year_from,
        year_to=model_in.year_to,
        is_active=model_in.is_active,
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="CREATE",
        entity="Model",
        entity_id=model.id,
        new_value={"name": model.name, "brand_id": model.brand_id},
        details=f"Created model {brand.name} {model.name}",
    )

    out = VehicleModelOut.model_validate(model)
    out.brand_name = brand.name
    return out


@router.put("/admin/{model_id}", response_model=VehicleModelOut)
def update_model(
    model_id: int,
    model_in: VehicleModelUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: update vehicle model"""
    model = db.query(VehicleModel).options(joinedload(VehicleModel.brand)).filter(VehicleModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    if model_in.name is not None:
        model.name = model_in.name.strip()
    if model_in.slug is not None:
        model.slug = model_in.slug.strip()
    if model_in.year_from is not None:
        model.year_from = model_in.year_from
    if model_in.year_to is not None:
        model.year_to = model_in.year_to
    if model_in.is_active is not None:
        model.is_active = model_in.is_active

    db.commit()
    db.refresh(model)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="UPDATE",
        entity="Model",
        entity_id=model.id,
        details=f"Updated model {model.name}",
    )

    out = VehicleModelOut.model_validate(model)
    out.brand_name = model.brand.name if model.brand else None
    return out
