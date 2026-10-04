import sys
from pathlib import Path
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models import (
    User,
    VehicleBrand,
    VehicleModel,
    Color,
    ColorType,
    Formula,
    FormulaStatus,
    FormulaSourceType,
    FormulaComponent,
)
from app.auth.security import get_password_hash, create_access_token

# Use in-memory SQLite for fast, isolated, robust unit and integration testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Pre-populate admin user
    admin = User(
        email="testadmin@paintformula.az",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test Paint Expert",
        is_active=True,
        is_superuser=True,
    )
    session.add(admin)

    # Pre-populate sample Toyota Camry 1G3
    toyota = VehicleBrand(name="Toyota", slug="toyota", country="Japan", is_active=True)
    session.add(toyota)
    session.flush()

    camry = VehicleModel(brand_id=toyota.id, name="Camry", slug="toyota-camry", year_from=2018, year_to=2024, is_active=True)
    session.add(camry)
    session.flush()

    color_1g3 = Color(
        brand_id=toyota.id,
        model_id=camry.id,
        color_code="1G3",
        color_name="Magnetic Gray",
        color_type=ColorType.METALLIC,
        paint_system="Basecoat",
        is_active=True,
    )
    session.add(color_1g3)
    session.flush()

    # Published formula 1000g
    formula = Formula(
        color_id=color_1g3.id,
        formula_name="Toyota 1G3 Magnetic Gray - Standard",
        variant_name="Standard",
        paint_system="Basecoat",
        base_total_amount=Decimal("1000.0000"),
        unit="g",
        status=FormulaStatus.PUBLISHED,
        version=1,
        source_type=FormulaSourceType.EXPERT_CREATED,
        created_by="testadmin@paintformula.az",
    )
    session.add(formula)
    session.flush()

    comps = [
        FormulaComponent(formula_id=formula.id, component_code="B001", component_name="White Base", amount=Decimal("350.0000"), unit="g", sort_order=0),
        FormulaComponent(formula_id=formula.id, component_code="B014", component_name="Black", amount=Decimal("220.0000"), unit="g", sort_order=1),
        FormulaComponent(formula_id=formula.id, component_code="M003", component_name="Metallic", amount=Decimal("180.0000"), unit="g", sort_order=2),
        FormulaComponent(formula_id=formula.id, component_code="K002", component_name="Deep Blue", amount=Decimal("100.0000"), unit="g", sort_order=3),
        FormulaComponent(formula_id=formula.id, component_code="X001", component_name="Binder", amount=Decimal("150.0000"), unit="g", sort_order=4),
    ]
    for c in comps:
        session.add(c)

    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token():
    return create_access_token(subject="testadmin@paintformula.az")


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
