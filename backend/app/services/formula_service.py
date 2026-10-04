from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.formula import Formula, FormulaStatus, FormulaSourceType
from app.models.component import FormulaComponent
from app.models.color import Color
from app.schemas.formula import FormulaCreate, FormulaUpdate
from app.services.audit_service import AuditService


class FormulaService:
    @staticmethod
    def get_formula_by_id(db: Session, formula_id: int, public_only: bool = False) -> Formula:
        query = (
            db.query(Formula)
            .options(
                joinedload(Formula.components),
                joinedload(Formula.color).joinedload(Color.brand),
                joinedload(Formula.color).joinedload(Color.model),
            )
            .filter(Formula.id == formula_id)
        )
        if public_only:
            query = query.filter(Formula.status == FormulaStatus.PUBLISHED)
        formula = query.first()
        if not formula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Formula with id {formula_id} not found" + (" or not published" if public_only else ""),
            )
        return formula

    @staticmethod
    def create_formula(db: Session, formula_in: FormulaCreate, user_email: str) -> Formula:
        # Check color exists
        color = db.query(Color).filter(Color.id == formula_in.color_id).first()
        if not color:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced Color not found.")

        # Check for duplicate formula with exact same color, variant and version
        duplicate = (
            db.query(Formula)
            .filter(
                Formula.color_id == formula_in.color_id,
                Formula.variant_name == formula_in.variant_name,
                Formula.version == formula_in.version,
            )
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A formula for this color with variant '{formula_in.variant_name}' and version {formula_in.version} already exists.",
            )

        # Validate components
        if formula_in.status in [FormulaStatus.VERIFIED, FormulaStatus.PUBLISHED]:
            if not formula_in.components:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot verify or publish a formula without components.",
                )
            calculated_sum = sum(comp.amount for comp in formula_in.components)
            if abs(calculated_sum - formula_in.base_total_amount) > Decimal("0.001"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Component sum ({calculated_sum}) does not match base total amount ({formula_in.base_total_amount}).",
                )

        # Create formula entity
        formula = Formula(
            color_id=formula_in.color_id,
            formula_name=formula_in.formula_name,
            variant_name=formula_in.variant_name,
            paint_system=formula_in.paint_system,
            base_total_amount=formula_in.base_total_amount,
            unit=formula_in.unit,
            status=formula_in.status,
            version=formula_in.version,
            source_type=formula_in.source_type,
            expert_notes=formula_in.expert_notes,
            preparation_notes=formula_in.preparation_notes,
            created_by=user_email,
        )
        db.add(formula)
        db.flush()

        # Add components
        for idx, comp_in in enumerate(formula_in.components):
            comp = FormulaComponent(
                formula_id=formula.id,
                component_code=comp_in.component_code,
                component_name=comp_in.component_name,
                amount=comp_in.amount,
                unit=comp_in.unit,
                sort_order=comp_in.sort_order if comp_in.sort_order is not None else idx,
                notes=comp_in.notes,
            )
            db.add(comp)

        db.commit()
        db.refresh(formula)

        # Audit log
        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="CREATE",
            entity="Formula",
            entity_id=formula.id,
            new_value={
                "formula_name": formula.formula_name,
                "color_id": formula.color_id,
                "variant": formula.variant_name,
                "version": formula.version,
                "status": formula.status.value,
                "components_count": len(formula_in.components),
            },
            details=f"Created formula {formula.formula_name} (v{formula.version})",
        )

        return FormulaService.get_formula_by_id(db, formula.id)

    @staticmethod
    def update_formula(db: Session, formula_id: int, formula_in: FormulaUpdate, user_email: str) -> Formula:
        formula = FormulaService.get_formula_by_id(db, formula_id)
        old_data = {
            "formula_name": formula.formula_name,
            "variant_name": formula.variant_name,
            "status": formula.status.value,
            "base_total_amount": str(formula.base_total_amount),
        }

        # Update attributes if provided
        if formula_in.formula_name is not None:
            formula.formula_name = formula_in.formula_name
        if formula_in.variant_name is not None:
            formula.variant_name = formula_in.variant_name
        if formula_in.paint_system is not None:
            formula.paint_system = formula_in.paint_system
        if formula_in.unit is not None:
            formula.unit = formula_in.unit
        if formula_in.source_type is not None:
            formula.source_type = formula_in.source_type
        if formula_in.expert_notes is not None:
            formula.expert_notes = formula_in.expert_notes
        if formula_in.preparation_notes is not None:
            formula.preparation_notes = formula_in.preparation_notes

        # If components updated
        if formula_in.components is not None:
            # Delete old components
            formula.components.clear()
            calculated_sum = Decimal("0.0000")
            for idx, comp_in in enumerate(formula_in.components):
                if comp_in.amount <= Decimal("0"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Component {comp_in.component_code} amount must be greater than zero.",
                    )
                calculated_sum += comp_in.amount
                comp = FormulaComponent(
                    formula_id=formula.id,
                    component_code=comp_in.component_code,
                    component_name=comp_in.component_name,
                    amount=comp_in.amount,
                    unit=comp_in.unit,
                    sort_order=comp_in.sort_order if comp_in.sort_order is not None else idx,
                    notes=comp_in.notes,
                )
                formula.components.append(comp)

            # Auto-align or validate base_total_amount
            if formula_in.base_total_amount is not None:
                formula.base_total_amount = formula_in.base_total_amount
            elif calculated_sum > 0:
                formula.base_total_amount = calculated_sum

        elif formula_in.base_total_amount is not None:
            formula.base_total_amount = formula_in.base_total_amount

        if formula_in.status is not None:
            FormulaService._apply_status_transition(formula, formula_in.status, user_email)
        elif formula.status in [FormulaStatus.VERIFIED, FormulaStatus.PUBLISHED]:
            FormulaService._validate_components(formula)

        db.commit()
        db.refresh(formula)

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="UPDATE",
            entity="Formula",
            entity_id=formula.id,
            old_value=old_data,
            new_value={
                "formula_name": formula.formula_name,
                "variant_name": formula.variant_name,
                "status": formula.status.value,
                "base_total_amount": str(formula.base_total_amount),
            },
            details=f"Updated formula {formula.formula_name}",
        )

        return FormulaService.get_formula_by_id(db, formula.id)

    @staticmethod
    def _apply_status_transition(formula: Formula, new_status: FormulaStatus, user_email: str):
        if new_status == FormulaStatus.VERIFIED:
            FormulaService._validate_components(formula)
            formula.verified_by = user_email
            formula.verified_at = datetime.now(timezone.utc)
        elif new_status == FormulaStatus.PUBLISHED:
            FormulaService._validate_components(formula)
            if not formula.verified_by:
                formula.verified_by = user_email
                formula.verified_at = datetime.now(timezone.utc)
        formula.status = new_status

    @staticmethod
    def _validate_components(formula: Formula):
        if not formula.components:
            raise HTTPException(status_code=400, detail="Cannot verify or publish a formula with no components.")
        component_total = sum((Decimal(str(component.amount)) for component in formula.components), Decimal("0"))
        base_total = Decimal(str(formula.base_total_amount))
        if abs(component_total - base_total) > Decimal("0.001"):
            raise HTTPException(
                status_code=400,
                detail=f"Component sum ({component_total}) does not match base total amount ({base_total}).",
            )

    @staticmethod
    def verify_formula(db: Session, formula_id: int, user_email: str) -> Formula:
        formula = FormulaService.get_formula_by_id(db, formula_id)
        old_status = formula.status.value
        FormulaService._apply_status_transition(formula, FormulaStatus.VERIFIED, user_email)
        db.commit()
        db.refresh(formula)

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="VERIFY",
            entity="Formula",
            entity_id=formula.id,
            old_value={"status": old_status},
            new_value={"status": formula.status.value, "verified_by": user_email},
            details=f"Verified formula {formula.formula_name}",
        )
        return formula

    @staticmethod
    def publish_formula(db: Session, formula_id: int, user_email: str) -> Formula:
        formula = FormulaService.get_formula_by_id(db, formula_id)
        old_status = formula.status.value
        FormulaService._apply_status_transition(formula, FormulaStatus.PUBLISHED, user_email)
        db.commit()
        db.refresh(formula)

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="PUBLISH",
            entity="Formula",
            entity_id=formula.id,
            old_value={"status": old_status},
            new_value={"status": formula.status.value},
            details=f"Published formula {formula.formula_name}",
        )
        return formula

    @staticmethod
    def deprecate_formula(db: Session, formula_id: int, user_email: str) -> Formula:
        formula = FormulaService.get_formula_by_id(db, formula_id)
        old_status = formula.status.value
        formula.status = FormulaStatus.DEPRECATED
        db.commit()
        db.refresh(formula)

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="DEPRECATE",
            entity="Formula",
            entity_id=formula.id,
            old_value={"status": old_status},
            new_value={"status": formula.status.value},
            details=f"Deprecated formula {formula.formula_name}",
        )
        return formula

    @staticmethod
    def create_new_version(db: Session, formula_id: int, user_email: str) -> Formula:
        """
        Creates a new version of an existing formula:
        - Version becomes current version + 1
        - Clones all components
        - Sets new version to DRAFT
        - Retains old formula intact in historical records
        """
        original = FormulaService.get_formula_by_id(db, formula_id)

        # Find highest existing version for this color and variant
        highest_version = (
            db.query(Formula.version)
            .filter(
                Formula.color_id == original.color_id,
                Formula.variant_name == original.variant_name,
            )
            .order_by(Formula.version.desc())
            .first()
        )
        new_version_num = (highest_version[0] if highest_version else original.version) + 1

        new_formula = Formula(
            color_id=original.color_id,
            formula_name=original.formula_name,
            variant_name=original.variant_name,
            paint_system=original.paint_system,
            base_total_amount=original.base_total_amount,
            unit=original.unit,
            status=FormulaStatus.DRAFT,
            version=new_version_num,
            source_type=FormulaSourceType.CORRECTED,
            expert_notes=f"Branched from Version {original.version}. {original.expert_notes or ''}".strip(),
            preparation_notes=original.preparation_notes,
            created_by=user_email,
        )
        db.add(new_formula)
        db.flush()

        # Clone components
        for comp in original.components:
            new_comp = FormulaComponent(
                formula_id=new_formula.id,
                component_code=comp.component_code,
                component_name=comp.component_name,
                amount=comp.amount,
                unit=comp.unit,
                sort_order=comp.sort_order,
                notes=comp.notes,
            )
            db.add(new_comp)

        db.commit()
        db.refresh(new_formula)

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="CREATE_VERSION",
            entity="Formula",
            entity_id=new_formula.id,
            old_value={"original_formula_id": original.id, "version": original.version},
            new_value={"new_formula_id": new_formula.id, "version": new_version_num},
            details=f"Created Version {new_version_num} from Version {original.version}",
        )

        return FormulaService.get_formula_by_id(db, new_formula.id)
