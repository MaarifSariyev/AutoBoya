def test_public_user_cannot_access_admin_brands(client):
    response = client.get("/api/brands/admin")
    assert response.status_code == 401


def test_unauthenticated_cannot_create_formula(client):
    response = client.post(
        "/api/formulas/admin",
        json={
            "color_id": 1,
            "formula_name": "Unauthorized Formula",
            "variant_name": "Standard",
            "base_total_amount": 1000,
            "components": [],
        },
    )
    assert response.status_code == 401


def test_admin_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testadmin@paintformula.az",
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testadmin@paintformula.az"


def test_admin_can_access_protected_endpoints(client, admin_headers):
    response = client.get("/api/brands/admin", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
