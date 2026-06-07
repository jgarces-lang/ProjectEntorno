import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from main import app, get_session, Categoria, Admin, Producto, hash_password


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    cats = [
        Categoria(nombre="Laptops"),
        Categoria(nombre="Smartphones"),
        Categoria(nombre="Audífonos"),
    ]
    for c in cats:
        session.add(c)
    session.flush()

    productos = [
        Producto(nombre="MacBook Pro 16\"", precio=2499.99, descripcion="Laptop potente", categoria_id=cats[0].id, imagen_url="", activo=True),
        Producto(nombre="iPhone 15", precio=1299.99, descripcion="Smartphone", categoria_id=cats[1].id, imagen_url="", activo=True),
        Producto(nombre="AirPods Pro", precio=249.99, descripcion="Audífonos", categoria_id=cats[2].id, imagen_url="", activo=False),
    ]
    for p in productos:
        session.add(p)

    admin = Admin(username="admin", password_hash=hash_password("admin123"))
    session.add(admin)
    session.commit()

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
