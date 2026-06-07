from main import Producto, Categoria


# ── 1. GET /api/categorias ──────────────────────────────
def test_listar_categorias(client):
    response = client.get("/api/categorias")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["nombre"] == "Laptops"


# ── 2. GET /api/productos ───────────────────────────────
def test_listar_productos(client):
    response = client.get("/api/productos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["nombre"] is not None
    assert data[0]["precio"] > 0


# ── 3. GET /api/productos con filtro de categoría ───────
def test_productos_por_categoria(client):
    response = client.get("/api/productos?categoria_id=1")
    assert response.status_code == 200
    data = response.json()
    for p in data:
        assert p["categoria_id"] == 1


# ── 4. GET /api/producto ─────────────────────────────────
def test_obtener_producto_por_id(client):
    response = client.get("/api/producto?id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "nombre" in data


# ── 5. GET /api/producto — 404 si no existe ──────────────
def test_producto_no_existe(client):
    response = client.get("/api/producto?id=99999")
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower()


# ── 6. POST /api/auth — login correcto ───────────────────
def test_login_admin_correcto(client):
    response = client.post("/api/auth", json={
        "username": "admin",
        "password": "admin123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["username"] == "admin"


# ── 7. POST /api/auth — login incorrecto ─────────────────
def test_login_admin_incorrecto(client):
    response = client.post("/api/auth", json={
        "username": "admin",
        "password": "wrongpass",
    })
    assert response.status_code == 401


# ── 8. POST /api/admin/productos — crear producto ────────
def test_crear_producto_admin(client):
    response = client.post("/api/admin/productos", json={
        "nombre": "Producto Test",
        "precio": 99.99,
        "descripcion": "Descripción test",
        "categoria_id": 1,
    }, headers={"Authorization": "Bearer admin-token-seguro"})
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Producto Test"
    assert data["precio"] == 99.99


# ── 9. POST /api/admin/productos — sin auth ──────────────
def test_crear_producto_sin_auth(client):
    response = client.post("/api/admin/productos", json={
        "nombre": "No Auth",
        "precio": 10,
    })
    assert response.status_code == 401


# ── 10. PUT /api/admin/productos/{id} — actualizar ──────
def test_actualizar_producto(client):
    response = client.put("/api/admin/productos/1", json={
        "precio": 1999.99,
    }, headers={"Authorization": "Bearer admin-token-seguro"})
    assert response.status_code == 200
    assert response.json()["precio"] == 1999.99


# ── 11. PUT /api/admin/productos/{id} — desactivar ──────
def test_desactivar_producto(client):
    response = client.put("/api/admin/productos/1", json={
        "activo": False,
    }, headers={"Authorization": "Bearer admin-token-seguro"})
    assert response.status_code == 200
    assert response.json()["activo"] is False


# ── 12. Producto inactivo no aparece en catálogo ─────────
def test_producto_inactivo_no_en_catalogo(client, session):
    p = session.get(Producto, 1)
    if p:
        p.activo = False
        session.add(p)
        session.commit()
    response = client.get("/api/productos")
    data = response.json()
    for prod in data:
        assert prod["id"] != 1
