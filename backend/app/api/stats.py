from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.brand import VehicleBrand
from app.models.model import VehicleModel
from app.models.color import Color
from app.models.component import ComponentLibrary
from app.models.formula import Formula, FormulaStatus
from app.models.user import User
from app.schemas.formula import FormulaOut
from app.api.formulas import _format_formula_out
from app.auth.deps import get_current_active_admin

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
) -> Dict[str, Any]:
    """Admin dashboard stats directly aggregated from database"""
    total_brands = db.query(func.count(VehicleBrand.id)).scalar() or 0
    total_models = db.query(func.count(VehicleModel.id)).scalar() or 0
    total_colors = db.query(func.count(Color.id)).scalar() or 0
    total_components = db.query(func.count(ComponentLibrary.id)).scalar() or 0
    total_formulas = db.query(func.count(Formula.id)).scalar() or 0

    published_formulas = (
        db.query(func.count(Formula.id)).filter(Formula.status == FormulaStatus.PUBLISHED).scalar() or 0
    )
    draft_formulas = (
        db.query(func.count(Formula.id)).filter(Formula.status == FormulaStatus.DRAFT).scalar() or 0
    )
    under_review_formulas = (
        db.query(func.count(Formula.id)).filter(Formula.status == FormulaStatus.UNDER_REVIEW).scalar() or 0
    )
    verified_formulas = (
        db.query(func.count(Formula.id)).filter(Formula.status == FormulaStatus.VERIFIED).scalar() or 0
    )
    deprecated_formulas = (
        db.query(func.count(Formula.id)).filter(Formula.status == FormulaStatus.DEPRECATED).scalar() or 0
    )

    recent_formulas = (
        db.query(Formula)
        .order_by(Formula.updated_at.desc())
        .limit(8)
        .all()
    )

    return {
        "total_brands": total_brands,
        "total_models": total_models,
        "total_colors": total_colors,
            "total_components": total_components,
        "total_formulas": total_formulas,
        "published_formulas": published_formulas,
        "draft_formulas": draft_formulas,
        "under_review_formulas": under_review_formulas,
        "verified_formulas": verified_formulas,
        "deprecated_formulas": deprecated_formulas,
        "recent_formulas": [_format_formula_out(f) for f in recent_formulas],
    }
