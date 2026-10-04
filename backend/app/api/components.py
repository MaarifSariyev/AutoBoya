from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.models.component import ComponentLibrary
from app.models.user import User
from app.schemas.component import ComponentLibraryCreate, ComponentLibraryUpdate, ComponentLibraryOut
from app.auth.deps import get_current_active_admin
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=List[ComponentLibraryOut])
def get_component_library(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List reusable components from library (for formula editor autocomplete)"""
    query = db.query(ComponentLibrary).filter(ComponentLibrary.is_active == True)
    if search:
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ComponentLibrary.code).like(term),
                func.lower(ComponentLibrary.name).like(term),
                func.lower(ComponentLibrary.brand).like(term),
            )
        )
    if category:
        query = query.filter(ComponentLibrary.category == category)
    return query.order_by(ComponentLibrary.code.asc()).all()


@router.get("/admin", response_model=List[ComponentLibraryOut])
def get_admin_component_library(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 500,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: list all components in library"""
    query = db.query(ComponentLibrary)
    if search:
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ComponentLibrary.code).like(term),
                func.lower(ComponentLibrary.name).like(term),
            )
        )
    return query.order_by(ComponentLibrary.code.asc()).offset(skip).limit(limit).all()


@router.post("/admin", response_model=ComponentLibraryOut, status_code=status.HTTP_201_CREATED)
def create_component(
    comp_in: ComponentLibraryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: add new component to library"""
    existing = db.query(ComponentLibrary).filter(ComponentLibrary.code.ilike(comp_in.code)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Component with code '{comp_in.code}' already exists.")

    comp = ComponentLibrary(
        code=comp_in.code.strip(),
        name=comp_in.name.strip(),
        brand=comp_in.brand,
        category=comp_in.category,
        unit=comp_in.unit,
        description=comp_in.description,
        is_active=comp_in.is_active,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="CREATE",
        entity="ComponentLibrary",
        entity_id=comp.id,
        new_value={"code": comp.code, "name": comp.name},
        details=f"Created component {comp.code} ({comp.name})",
    )

    return comp


@router.put("/admin/{comp_id}", response_model=ComponentLibraryOut)
def update_component(
    comp_id: int,
    comp_in: ComponentLibraryUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: update component in library"""
    comp = db.query(ComponentLibrary).filter(ComponentLibrary.id == comp_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found.")

    if comp_in.code is not None:
        comp.code = comp_in.code.strip()
    if comp_in.name is not None:
        comp.name = comp_in.name.strip()
    if comp_in.brand is not None:
        comp.brand = comp_in.brand
    if comp_in.category is not None:
        comp.category = comp_in.category
    if comp_in.unit is not None:
        comp.unit = comp_in.unit
    if comp_in.description is not None:
        comp.description = comp_in.description
    if comp_in.is_active is not None:
        comp.is_active = comp_in.is_active

    db.commit()
    db.refresh(comp)

    AuditService.log_action(
        db=db,
        user_email=admin.email,
        action="UPDATE",
        entity="ComponentLibrary",
        entity_id=comp.id,
        details=f"Updated component {comp.code}",
    )

    return comp
