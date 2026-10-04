from decimal import Decimal
from app.models.formula import Formula
from app.services.calculation_service import CalculationService


def test_calculation_service_500g(db_session):
    formula = db_session.query(Formula).first()
    assert formula is not None

    res = CalculationService.calculate(formula=formula, target_amount=Decimal("500.0000"), unit="g")
    assert res.target_amount == Decimal("500.0000")
    assert res.total == Decimal("500.0000")
    assert res.factor == Decimal("0.500000")

    comp_map = {c.component_code: c.amount for c in res.components}
    assert comp_map["B001"] == Decimal("175.0000")
    assert comp_map["B014"] == Decimal("110.0000")
    assert comp_map["M003"] == Decimal("90.0000")
    assert comp_map["K002"] == Decimal("50.0000")
    assert comp_map["X001"] == Decimal("75.0000")


def test_calculation_service_250g(db_session):
    formula = db_session.query(Formula).first()
    res = CalculationService.calculate(formula=formula, target_amount=Decimal("250.0000"), unit="g")
    assert res.total == Decimal("250.0000")
    assert res.factor == Decimal("0.250000")

    comp_map = {c.component_code: c.amount for c in res.components}
    assert comp_map["B001"] == Decimal("87.5000")
    assert comp_map["B014"] == Decimal("55.0000")
    assert comp_map["M003"] == Decimal("45.0000")
    assert comp_map["K002"] == Decimal("25.0000")
    assert comp_map["X001"] == Decimal("37.5000")


def test_calculation_service_100g(db_session):
    formula = db_session.query(Formula).first()
    res = CalculationService.calculate(formula=formula, target_amount=Decimal("100.0000"), unit="g")
    assert res.total == Decimal("100.0000")
    assert res.factor == Decimal("0.100000")

    comp_map = {c.component_code: c.amount for c in res.components}
    assert comp_map["B001"] == Decimal("35.0000")
    assert comp_map["B014"] == Decimal("22.0000")
    assert comp_map["M003"] == Decimal("18.0000")
    assert comp_map["K002"] == Decimal("10.0000")
    assert comp_map["X001"] == Decimal("15.0000")


def test_calculation_service_custom_decimal(db_session):
    formula = db_session.query(Formula).first()
    target = Decimal("333.3333")
    res = CalculationService.calculate(formula=formula, target_amount=target, unit="g")
    assert abs(res.total - target) < Decimal("0.01")


def test_calculation_api_endpoint(client, db_session):
    formula = db_session.query(Formula).first()
    response = client.post(
        f"/api/formulas/{formula.id}/calculate",
        json={"target_amount": 500, "unit": "g"},
    )
    assert response.status_code == 200
    data = response.json()
    assert float(data["total"]) == 500.0
    assert float(data["target_amount"]) == 500.0
    assert len(data["components"]) == 5
