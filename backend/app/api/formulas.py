from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.formula import Formula, FormulaStatus
from app.models.user import User
from app.schemas.formula import FormulaCreate, FormulaUpdate, FormulaOut, FormulaSummaryOut
from app.schemas.calculation import CalculationRequest, CalculationResponse
from app.services.formula_service import FormulaService
from app.services.calculation_service import CalculationService
from app.services.search_service import SearchService
from app.services.pdf_service import PDFService
from app.auth.deps import get_current_active_admin

router = APIRouter()


def _format_formula_out(f: Formula) -> FormulaOut:
    out = FormulaOut.model_validate(f)
    if f.color:
        out.color_code = f.color.color_code
        out.color_name = f.color.color_name
        out.color_type = f.color.color_type.value if f.color.color_type else None
        if f.color.brand:
            out.brand_name = f.color.brand.name
        if f.color.model:
            out.model_name = f.color.model.name
    return out


# ==========================================
# Public Formula Endpoints (PUBLISHED only)
# ==========================================

@router.get("/search", response_model=List[FormulaOut])
def search_formulas(
    color_code: Optional[str] = None,
    color_name: Optional[str] = None,
    brand_id: Optional[int] = None,
    brand_name: Optional[str] = None,
    model_id: Optional[int] = None,
    model_name: Optional[str] = None,
    year: Optional[int] = None,
    paint_system: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Public search: returns only PUBLISHED formulas.
    Supports partial/exact color code, color name, vehicle brand, model, year.
    Variants are returned cleanly so users can choose between them.
    """
    formulas = SearchService.search_public_formulas(
        db=db,
        color_code=color_code,
        color_name=color_name,
        brand_id=brand_id,
        brand_name=brand_name,
        model_id=model_id,
        model_name=model_name,
        year=year,
        paint_system=paint_system,
        limit=limit,
        offset=offset,
    )
    return [_format_formula_out(f) for f in formulas]


@router.get("/{formula_id}", response_model=FormulaOut)
def get_public_formula(formula_id: int, db: Session = Depends(get_db)):
    """Public detail: only viewable if formula is PUBLISHED"""
    f = FormulaService.get_formula_by_id(db, formula_id, public_only=True)
    return _format_formula_out(f)


@router.post("/{formula_id}/calculate", response_model=CalculationResponse)
def calculate_formula_quantities(
    formula_id: int,
    calc_req: CalculationRequest,
    db: Session = Depends(get_db),
):
    """
    Core feature: proportionally recalculates formula components
    for a given target quantity using exact Decimal arithmetic.
    """
    # Public calculation allows published formulas; if user is admin, allow draft as well
    f = db.query(Formula).filter(Formula.id == formula_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Formula not found")
    if f.status != FormulaStatus.PUBLISHED:
        # Check if published or raise 404
        raise HTTPException(status_code=404, detail="Formula not found or not published.")

    return CalculationService.calculate(
        formula=f,
        target_amount=calc_req.target_amount,
        unit=calc_req.unit,
    )


@router.get("/{formula_id}/pdf")
def download_formula_pdf(
    formula_id: int,
    target_amount: Optional[Decimal] = Query(None, gt=0),
    unit: str = Query("g"),
    db: Session = Depends(get_db),
):
    """Generates a professional printable PDF formula sheet"""
    f = FormulaService.get_formula_by_id(db, formula_id, public_only=True)
    calc_amount = target_amount or f.base_total_amount
    calc_data = CalculationService.calculate(formula=f, target_amount=calc_amount, unit=unit)

    pdf_bytes = PDFService.generate_formula_sheet_pdf(
        calc_data=calc_data,
        preparation_notes=f.preparation_notes,
    )

    filename = f"Formula_{f.color.color_code if f.color else 'Paint'}_{calc_amount}{unit}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


# ==========================================
# Admin Formula Endpoints
# ==========================================

@router.get("/admin/all", response_model=List[FormulaOut])
def get_admin_formulas(
    query_text: Optional[str] = None,
    status: Optional[FormulaStatus] = None,
    brand_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: list formulas across all statuses (Draft, Under Review, Verified, Published, Deprecated)"""
    formulas = SearchService.admin_search_formulas(
        db=db,
        query_text=query_text,
        status=status,
        brand_id=brand_id,
        limit=limit,
        offset=offset,
    )
    return [_format_formula_out(f) for f in formulas]


@router.get("/admin/{formula_id}", response_model=FormulaOut)
def get_admin_formula_detail(
    formula_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: get formula by id regardless of status"""
    f = FormulaService.get_formula_by_id(db, formula_id, public_only=False)
    return _format_formula_out(f)


@router.post("/admin", response_model=FormulaOut, status_code=status.HTTP_201_CREATED)
def create_formula(
    formula_in: FormulaCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: create new formula with components and validation"""
    f = FormulaService.create_formula(db=db, formula_in=formula_in, user_email=admin.email)
    return _format_formula_out(f)


@router.put("/admin/{formula_id}", response_model=FormulaOut)
def update_formula(
    formula_id: int,
    formula_in: FormulaUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: update formula details and components"""
    f = FormulaService.update_formula(db=db, formula_id=formula_id, formula_in=formula_in, user_email=admin.email)
    return _format_formula_out(f)


@router.post("/admin/{formula_id}/verify", response_model=FormulaOut)
def verify_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: transition formula status to VERIFIED"""
    f = FormulaService.verify_formula(db=db, formula_id=formula_id, user_email=admin.email)
    return _format_formula_out(f)


@router.post("/admin/{formula_id}/publish", response_model=FormulaOut)
def publish_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: transition formula status to PUBLISHED"""
    f = FormulaService.publish_formula(db=db, formula_id=formula_id, user_email=admin.email)
    return _format_formula_out(f)


@router.post("/admin/{formula_id}/deprecate", response_model=FormulaOut)
def deprecate_formula(
    formula_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: deprecate formula instead of deleting (preserves historical data)"""
    f = FormulaService.deprecate_formula(db=db, formula_id=formula_id, user_email=admin.email)
    return _format_formula_out(f)


@router.post("/admin/{formula_id}/version", response_model=FormulaOut)
def create_new_formula_version(
    formula_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
):
    """Admin: creates version N+1 from existing formula, preserving previous version"""
    f = FormulaService.create_new_version(db=db, formula_id=formula_id, user_email=admin.email)
    return _format_formula_out(f)
