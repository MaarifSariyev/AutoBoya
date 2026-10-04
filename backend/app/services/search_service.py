from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func

from app.models.formula import Formula, FormulaStatus
from app.models.color import Color
from app.models.brand import VehicleBrand
from app.models.model import VehicleModel


class SearchService:
    @staticmethod
    def search_public_formulas(
        db: Session,
        color_code: Optional[str] = None,
        color_name: Optional[str] = None,
        brand_id: Optional[int] = None,
        brand_name: Optional[str] = None,
        model_id: Optional[int] = None,
        model_name: Optional[str] = None,
        year: Optional[int] = None,
        paint_system: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Formula]:
        """
        Public search: only queries PUBLISHED formulas.
        Supports exact/partial color code, color name, brand, model, year range.
        """
        query = (
            db.query(Formula)
            .join(Formula.color)
            .join(Color.brand)
            .outerjoin(Color.model)
            .options(
                joinedload(Formula.components),
                joinedload(Formula.color).joinedload(Color.brand),
                joinedload(Formula.color).joinedload(Color.model),
            )
            .filter(Formula.status == FormulaStatus.PUBLISHED)
        )

        # Color code filter (case-insensitive, exact or partial match)
        if color_code:
            code_clean = color_code.strip()
            # If user entered exact code or partial code
            query = query.filter(
                or_(
                    func.lower(Color.color_code) == code_clean.lower(),
                    func.lower(Color.color_code).like(f"%{code_clean.lower()}%"),
                )
            )

        # Color name filter
        if color_name:
            query = query.filter(func.lower(Color.color_name).like(f"%{color_name.strip().lower()}%"))

        # Brand filter
        if brand_id:
            query = query.filter(Color.brand_id == brand_id)
        elif brand_name:
            query = query.filter(func.lower(VehicleBrand.name).like(f"%{brand_name.strip().lower()}%"))

        # Model filter
        if model_id:
            query = query.filter(Color.model_id == model_id)
        elif model_name:
            query = query.filter(func.lower(VehicleModel.name).like(f"%{model_name.strip().lower()}%"))

        # Year filter (within model's year_from and year_to if specified)
        if year:
            query = query.filter(
                or_(
                    Color.model_id.is_(None),  # brand-level color applies to all years
                    and_(
                        or_(VehicleModel.year_from.is_(None), VehicleModel.year_from <= year),
                        or_(VehicleModel.year_to.is_(None), VehicleModel.year_to >= year),
                    ),
                )
            )

        # Paint system filter
        if paint_system:
            query = query.filter(func.lower(Formula.paint_system) == paint_system.strip().lower())

        # Sort order: Brand name, Color code, Variant name, Version desc
        query = query.order_by(
            VehicleBrand.name.asc(),
            Color.color_code.asc(),
            Formula.variant_name.asc(),
            Formula.version.desc(),
        )

        return query.offset(offset).limit(limit).all()

    @staticmethod
    def admin_search_formulas(
        db: Session,
        query_text: Optional[str] = None,
        status: Optional[FormulaStatus] = None,
        brand_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Formula]:
        """
        Admin search across all formula statuses.
        """
        query = (
            db.query(Formula)
            .join(Formula.color)
            .join(Color.brand)
            .outerjoin(Color.model)
            .options(
                joinedload(Formula.components),
                joinedload(Formula.color).joinedload(Color.brand),
                joinedload(Formula.color).joinedload(Color.model),
            )
        )

        if status:
            query = query.filter(Formula.status == status)

        if brand_id:
            query = query.filter(Color.brand_id == brand_id)

        if query_text:
            clean = f"%{query_text.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Formula.formula_name).like(clean),
                    func.lower(Formula.variant_name).like(clean),
                    func.lower(Color.color_code).like(clean),
                    func.lower(Color.color_name).like(clean),
                    func.lower(VehicleBrand.name).like(clean),
                    func.lower(VehicleModel.name).like(clean),
                )
            )

        query = query.order_by(Formula.updated_at.desc())
        return query.offset(offset).limit(limit).all()
