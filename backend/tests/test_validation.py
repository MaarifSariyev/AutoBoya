import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.models.formula import FormulaStatus, FormulaSourceType
from app.schemas.formula import FormulaCreate, FormulaUpdate
from app.schemas.component import FormulaComponentCreate
from app.services.formula_service import FormulaService
from app.models.color import Color
from app.models.formula import Formula
from app.models.component import FormulaComponent
from fastapi import HTTPException
from pydantic import ValidationError
from app.core.config import Settings


def test_reject_negative_component_amount():
    with pytest.raises(ValidationError):
        FormulaComponentCreate(
            component_code="B001",
            component_name="White Base",
            amount=Decimal("-10.0000"),
            unit="g",
        )


def test_reject_zero_component_amount():
    with pytest.raises(ValidationError):
        FormulaComponentCreate(
            component_code="B001",
            component_name="White Base",
            amount=Decimal("0.0000"),
            unit="g",
        )


def test_reject_mismatched_formula_total_on_published():
    # If status is PUBLISHED, component amounts sum must equal base_total_amount
    with pytest.raises(ValidationError) as exc_info:
        FormulaCreate(
            color_id=1,
            formula_name="Test Formula",
            variant_name="Standard",
            paint_system="Basecoat",
            base_total_amount=Decimal("1000.0000"),
            unit="g",
            status=FormulaStatus.PUBLISHED,
            components=[
                FormulaComponentCreate(component_code="B001", component_name="White", amount=Decimal("300.0000"), unit="g"),
                FormulaComponentCreate(component_code="B014", component_name="Black", amount=Decimal("200.0000"), unit="g"),
            ],
        )
    assert "Component amounts sum to 500" in str(exc_info.value)


def test_reject_duplicate_formula(db_session):
    # Already seeded with Toyota 1G3 Standard v1
    formula_in = FormulaCreate(
        color_id=1,
        formula_name="Duplicate Attempt",
        variant_name="Standard",
        version=1,
        paint_system="Basecoat",
        base_total_amount=Decimal("1000.0000"),
        unit="g",
        status=FormulaStatus.DRAFT,
        components=[
            FormulaComponentCreate(component_code="B001", component_name="White", amount=Decimal("1000.0000"), unit="g")
        ],
    )
    with pytest.raises(HTTPException) as exc_info:
        FormulaService.create_formula(db=db_session, formula_in=formula_in, user_email="test@test.com")
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_cannot_publish_formula_with_mismatched_component_total(db_session):
    color = db_session.query(Color).first()
    formula = Formula(
        color_id=color.id,
        formula_name="Mismatched Formula",
        variant_name="Mismatched",
        base_total_amount=Decimal("100.0000"),
        status=FormulaStatus.DRAFT,
        source_type=FormulaSourceType.EXPERT_CREATED,
    )
    db_session.add(formula)
    db_session.flush()
    db_session.add(
        FormulaComponent(
            formula_id=formula.id,
            component_code="B001",
            component_name="White Base",
            amount=Decimal("50.0000"),
            unit="g",
            sort_order=0,
        )
    )
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        FormulaService.publish_formula(db_session, formula.id, "testadmin@paintformula.az")

    assert exc_info.value.status_code == 400
    assert "does not match base total amount" in exc_info.value.detail


def test_cannot_change_total_of_published_formula_without_matching_components(db_session):
    formula = db_session.query(Formula).filter(Formula.status == FormulaStatus.PUBLISHED).first()

    with pytest.raises(HTTPException) as exc_info:
        FormulaService.update_formula(
            db_session,
            formula.id,
            FormulaUpdate(base_total_amount=Decimal("900.0000")),
            "testadmin@paintformula.az",
        )

    assert exc_info.value.status_code == 400


def test_color_update_can_clear_vehicle_model(client, admin_headers):
    response = client.put("/api/colors/admin/1", headers=admin_headers, json={"model_id": None})

    assert response.status_code == 200
    assert response.json()["model_id"] is None


def test_production_settings_reject_default_secrets():
    with pytest.raises(ValidationError, match="Production SECRET_KEY"):
        Settings(_env_file=None, ENVIRONMENT="production")


def test_production_settings_accept_unique_secrets():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        SECRET_KEY="a-unique-production-secret-key-with-more-than-32-characters",
        ADMIN_PASSWORD="a-unique-production-admin-password",
    )

    assert settings.ENVIRONMENT == "production"
