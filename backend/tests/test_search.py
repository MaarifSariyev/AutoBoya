from decimal import Decimal
from app.models.formula import Formula, FormulaStatus, FormulaSourceType
from app.models.component import FormulaComponent
from app.services.search_service import SearchService


def test_search_exact_color_code(db_session):
    results = SearchService.search_public_formulas(db=db_session, color_code="1G3")
    assert len(results) == 1
    assert results[0].color.color_code == "1G3"
    assert results[0].color.brand.name == "Toyota"


def test_search_partial_color_code(db_session):
    results = SearchService.search_public_formulas(db=db_session, color_code="1G")
    assert len(results) == 1
    assert results[0].color.color_code == "1G3"


def test_search_brand_and_model(db_session):
    results = SearchService.search_public_formulas(db=db_session, brand_name="Toyota", model_name="Camry")
    assert len(results) == 1
    assert results[0].color.color_name == "Magnetic Gray"


def test_search_brand_and_color_code(db_session):
    results = SearchService.search_public_formulas(db=db_session, brand_name="Toyota", color_code="1G3")
    assert len(results) == 1


def test_unpublished_formula_not_returned_in_public_search(db_session):
    # Add a draft formula
    draft_formula = Formula(
        color_id=1,
        formula_name="Toyota 1G3 Magnetic Gray - Secret Draft",
        variant_name="Secret Variant",
        paint_system="Basecoat",
        base_total_amount=Decimal("1000.0000"),
        unit="g",
        status=FormulaStatus.DRAFT,
        version=1,
        source_type=FormulaSourceType.EXPERT_CREATED,
        created_by="testadmin@paintformula.az",
    )
    db_session.add(draft_formula)
    db_session.flush()

    comp = FormulaComponent(formula_id=draft_formula.id, component_code="B001", component_name="White", amount=Decimal("1000.0000"), unit="g")
    db_session.add(comp)
    db_session.commit()

    # Public search should ONLY return the published one, not the secret draft
    results = SearchService.search_public_formulas(db=db_session, color_code="1G3")
    assert len(results) == 1
    assert results[0].variant_name == "Standard"
    assert results[0].status == FormulaStatus.PUBLISHED
