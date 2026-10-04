import io
import uuid
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from app.models.brand import VehicleBrand
from app.models.model import VehicleModel
from app.models.color import Color, ColorType
from app.models.formula import Formula, FormulaStatus, FormulaSourceType
from app.models.component import FormulaComponent, ComponentLibrary
from app.schemas.import_schema import ImportRow, ImportPreviewResponse, ImportResultResponse
from app.services.audit_service import AuditService

# In-memory storage for active pending import batches (keyed by batch_id)
# This allows complete review before committing to the database.
_PENDING_BATCHES: Dict[str, List[ImportRow]] = {}


class ImportService:
    @staticmethod
    def parse_and_validate_file(file_contents: bytes, filename: str, db: Session) -> ImportPreviewResponse:
        batch_id = str(uuid.uuid4())

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_contents))
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(file_contents))
            else:
                return ImportPreviewResponse(
                    batch_id=batch_id,
                    total_rows=0,
                    valid_rows=0,
                    invalid_rows=0,
                    total_formulas_detected=0,
                    errors=["Unsupported file format. Please upload a CSV or XLSX file."],
                    sample_preview=[],
                    can_proceed=False,
                )
        except Exception as e:
            return ImportPreviewResponse(
                batch_id=batch_id,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                total_formulas_detected=0,
                errors=[f"Failed to parse file: {str(e)}"],
                sample_preview=[],
                can_proceed=False,
            )

        # Standardize column headers (lowercase, trimmed)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        required_columns = ["brand", "color_code", "color_name", "component_code", "component_name", "amount"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ImportPreviewResponse(
                batch_id=batch_id,
                total_rows=len(df),
                valid_rows=0,
                invalid_rows=len(df),
                total_formulas_detected=0,
                errors=[f"Missing required columns: {', '.join(missing_columns)}"],
                sample_preview=[],
                can_proceed=False,
            )

        rows: List[ImportRow] = []
        valid_count = 0
        invalid_count = 0
        unique_formulas = set()

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed, row 1 is header
            errors: List[str] = []
            warnings: List[str] = []

            # Extract fields with fallbacks
            brand_val = str(row.get("brand", "")).strip()
            model_val = str(row.get("model", "")).strip() if pd.notna(row.get("model")) else None
            year_val = None
            if "year" in df.columns and pd.notna(row.get("year")):
                try:
                    year_val = int(row.get("year"))
                except ValueError:
                    errors.append("Invalid year value.")

            color_code_val = str(row.get("color_code", "")).strip()
            color_name_val = str(row.get("color_name", "")).strip()
            color_type_val = str(row.get("color_type", "Metallic")).strip().capitalize() if pd.notna(row.get("color_type")) else "Metallic"
            paint_system_val = str(row.get("paint_system", "Basecoat")).strip() if pd.notna(row.get("paint_system")) else "Basecoat"
            variant_val = str(row.get("variant", "Standard")).strip() if pd.notna(row.get("variant")) else "Standard"
            comp_code_val = str(row.get("component_code", "")).strip()
            comp_name_val = str(row.get("component_name", "")).strip()
            unit_val = str(row.get("unit", "g")).strip() if pd.notna(row.get("unit")) else "g"

            # Validate amount
            amount_val = Decimal("0")
            raw_amount = row.get("amount")
            if pd.isna(raw_amount):
                errors.append("Component amount is missing.")
            else:
                try:
                    amount_val = Decimal(str(raw_amount).strip())
                    if amount_val <= Decimal("0"):
                        errors.append("Component amount must be strictly greater than 0.")
                except InvalidOperation:
                    errors.append(f"Invalid numeric amount '{raw_amount}'.")

            # Check required string fields
            if not brand_val or brand_val == "nan":
                errors.append("Brand name is required.")
            if not color_code_val or color_code_val == "nan":
                errors.append("Color code is required.")
            if not color_name_val or color_name_val == "nan":
                errors.append("Color name is required.")
            if not comp_code_val or comp_code_val == "nan":
                errors.append("Component code is required.")
            if not comp_name_val or comp_name_val == "nan":
                errors.append("Component name is required.")

            formula_key = (brand_val, color_code_val, paint_system_val, variant_val)
            unique_formulas.add(formula_key)

            is_valid = len(errors) == 0
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            rows.append(
                ImportRow(
                    row_number=row_num,
                    brand=brand_val,
                    model=model_val if model_val != "nan" else None,
                    year=year_val,
                    color_code=color_code_val,
                    color_name=color_name_val,
                    color_type=color_type_val,
                    paint_system=paint_system_val,
                    variant=variant_val,
                    component_code=comp_code_val,
                    component_name=comp_name_val,
                    amount=amount_val,
                    unit=unit_val,
                    status="DRAFT",
                    is_valid=is_valid,
                    errors=errors,
                    warnings=warnings,
                )
            )

        # Store in pending batches
        _PENDING_BATCHES[batch_id] = rows

        return ImportPreviewResponse(
            batch_id=batch_id,
            total_rows=len(rows),
            valid_rows=valid_count,
            invalid_rows=invalid_count,
            total_formulas_detected=len(unique_formulas),
            errors=[f"Row {r.row_number}: {', '.join(r.errors)}" for r in rows if not r.is_valid][:15],
            sample_preview=rows[:20],
            can_proceed=(valid_count > 0 and invalid_count == 0),
        )

    @staticmethod
    def commit_import(batch_id: str, db: Session, user_email: str) -> ImportResultResponse:
        rows = _PENDING_BATCHES.get(batch_id)
        if not rows:
            raise ValueError("Import batch expired or not found. Please upload the file again.")

        # Ensure all rows valid
        invalid_rows = [r for r in rows if not r.is_valid]
        if invalid_rows:
            raise ValueError(f"Cannot commit batch with {len(invalid_rows)} invalid rows.")

        brands_created = 0
        models_created = 0
        colors_created = 0
        formulas_created = 0
        components_created = 0

        # Group rows by Formula: (brand, model, color_code, color_name, color_type, paint_system, variant)
        formulas_map: Dict[Tuple, List[ImportRow]] = {}
        for r in rows:
            key = (r.brand, r.model, r.year, r.color_code, r.color_name, r.color_type, r.paint_system, r.variant)
            if key not in formulas_map:
                formulas_map[key] = []
            formulas_map[key].append(r)

        for key, comp_rows in formulas_map.items():
            brand_name, model_name, year, color_code, color_name, color_type_str, paint_system, variant = key

            # 1. Brand
            brand = db.query(VehicleBrand).filter(VehicleBrand.name.ilike(brand_name)).first()
            if not brand:
                slug = brand_name.lower().replace(" ", "-").replace("/", "-")
                brand = VehicleBrand(name=brand_name, slug=slug, is_active=True)
                db.add(brand)
                db.flush()
                brands_created += 1

            # 2. Model (if specified)
            model = None
            if model_name:
                model = (
                    db.query(VehicleModel)
                    .filter(VehicleModel.brand_id == brand.id, VehicleModel.name.ilike(model_name))
                    .first()
                )
                if not model:
                    model_slug = f"{brand.slug}-{model_name.lower().replace(' ', '-')}"
                    model = VehicleModel(
                        brand_id=brand.id,
                        name=model_name,
                        slug=model_slug,
                        year_from=year,
                        year_to=year,
                        is_active=True,
                    )
                    db.add(model)
                    db.flush()
                    models_created += 1

            # 3. Color
            color = (
                db.query(Color)
                .filter(
                    Color.brand_id == brand.id,
                    Color.color_code.ilike(color_code),
                    Color.paint_system.ilike(paint_system),
                )
                .first()
            )
            if not color:
                # Resolve ColorType enum safely
                try:
                    c_type = ColorType(color_type_str)
                except Exception:
                    c_type = ColorType.METALLIC

                color = Color(
                    brand_id=brand.id,
                    model_id=model.id if model else None,
                    color_code=color_code,
                    color_name=color_name,
                    color_type=c_type,
                    paint_system=paint_system,
                    is_active=True,
                )
                db.add(color)
                db.flush()
                colors_created += 1

            # 4. Formula
            total_sum = sum(cr.amount for cr in comp_rows)
            formula_name = f"{brand.name} {color.color_code} {color.color_name} - {variant}"

            # Check if formula exists
            existing_formula = (
                db.query(Formula)
                .filter(
                    Formula.color_id == color.id,
                    Formula.variant_name == variant,
                )
                .order_by(Formula.version.desc())
                .first()
            )
            version = (existing_formula.version + 1) if existing_formula else 1

            formula = Formula(
                color_id=color.id,
                formula_name=formula_name,
                variant_name=variant,
                paint_system=paint_system,
                base_total_amount=total_sum,
                unit=comp_rows[0].unit,
                status=FormulaStatus.DRAFT,
                version=version,
                source_type=FormulaSourceType.IMPORTED,
                created_by=user_email,
            )
            db.add(formula)
            db.flush()
            formulas_created += 1

            # 5. Formula components & ComponentLibrary sync
            for idx, cr in enumerate(comp_rows):
                fc = FormulaComponent(
                    formula_id=formula.id,
                    component_code=cr.component_code,
                    component_name=cr.component_name,
                    amount=cr.amount,
                    unit=cr.unit,
                    sort_order=idx,
                )
                db.add(fc)
                components_created += 1

                # Ensure component in ComponentLibrary
                lib_comp = db.query(ComponentLibrary).filter(ComponentLibrary.code == cr.component_code).first()
                if not lib_comp:
                    lib_comp = ComponentLibrary(
                        code=cr.component_code,
                        name=cr.component_name,
                        unit=cr.unit,
                        is_active=True,
                    )
                    db.add(lib_comp)

        db.commit()

        # Clean up batch memory
        del _PENDING_BATCHES[batch_id]

        AuditService.log_action(
            db=db,
            user_email=user_email,
            action="IMPORT",
            entity="ImportBatch",
            entity_id=batch_id,
            details=f"Imported {formulas_created} formulas ({components_created} components) across {brands_created} new brands.",
        )

        return ImportResultResponse(
            brands_created=brands_created,
            models_created=models_created,
            colors_created=colors_created,
            formulas_created=formulas_created,
            components_created=components_created,
            message="Data import completed successfully.",
        )
