from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import hashlib
import os

load_dotenv()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Modelos ──────────────────────────────────────────────
class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)


class Producto(SQLModel, table=True):
    __tablename__ = "productos"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    precio: float
    descripcion: str = Field(default="")
    categoria_id: int | None = Field(default=None, foreign_key="categorias.id")
    imagen_url: str = Field(default="")
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Admin(SQLModel, table=True):
    __tablename__ = "admins"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str


# ── Schemas ──────────────────────────────────────────────
class ProductoOut(SQLModel):
    id: int
    nombre: str
    precio: float
    descripcion: str
    categoria_id: int | None
    categoria_nombre: str | None = None
    imagen_url: str
    activo: bool


class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    descripcion: str = ""
    categoria_id: int | None = None
    imagen_url: str = ""


class ProductoUpdate(BaseModel):
    nombre: str | None = None
    precio: float | None = None
    descripcion: str | None = None
    categoria_id: int | None = None
    imagen_url: str | None = None
    activo: bool | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class CategoriaOut(SQLModel):
    id: int
    nombre: str


# ── Base de datos ─────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-token-seguro")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def seed_data():
    with Session(engine) as session:
        existing = session.exec(select(Categoria)).first()
        if existing:
            return
        categorias = [
            Categoria(nombre="Laptops"),
            Categoria(nombre="Smartphones"),
            Categoria(nombre="Audífonos"),
            Categoria(nombre="Accesorios"),
            Categoria(nombre="Componentes"),
        ]
        for cat in categorias:
            session.add(cat)
        session.flush()

        productos = [
            Producto(nombre="MacBook Pro 16\" M3", precio=2499.99, descripcion="Chip M3, 36GB RAM, 1TB SSD", categoria_id=1, imagen_url="https://placehold.co/400x300?text=MacBook+Pro", activo=True),
            Producto(nombre="Dell XPS 15", precio=1899.99, descripcion="Intel i9, 32GB RAM, 1TB SSD", categoria_id=1, imagen_url="https://placehold.co/400x300?text=Dell+XPS", activo=True),
            Producto(nombre="iPhone 15 Pro Max", precio=1299.99, descripcion="256GB, Titanio Natural", categoria_id=2, imagen_url="https://placehold.co/400x300?text=iPhone+15", activo=True),
            Producto(nombre="Samsung Galaxy S24 Ultra", precio=1199.99, descripcion="512GB, S Pen incluido", categoria_id=2, imagen_url="https://placehold.co/400x300?text=Galaxy+S24", activo=True),
            Producto(nombre="AirPods Pro 2", precio=249.99, descripcion="Cancelación de ruido activa, USB-C", categoria_id=3, imagen_url="https://placehold.co/400x300?text=AirPods+Pro", activo=True),
            Producto(nombre="Sony WH-1000XM5", precio=349.99, descripcion="Audífonos inalámbricos con ANC", categoria_id=3, imagen_url="https://placehold.co/400x300?text=Sony+WH-1000XM5", activo=True),
            Producto(nombre="Logitech MX Master 3S", precio=99.99, descripcion="Mouse ergonómico inalámbrico", categoria_id=4, imagen_url="https://placehold.co/400x300?text=MX+Master", activo=True),
            Producto(nombre="Teclado Mecánico Keychron Q1", precio=179.99, descripcion="Teclado mecánico 75%, hot-swappable", categoria_id=4, imagen_url="https://placehold.co/400x300?text=Keychron+Q1", activo=True),
            Producto(nombre="NVIDIA RTX 4090", precio=1799.99, descripcion="24GB GDDR6X, 4nm", categoria_id=5, imagen_url="https://placehold.co/400x300?text=RTX+4090", activo=True),
            Producto(nombre="AMD Ryzen 9 7950X", precio=699.99, descripcion="16 núcleos, 32 hilos, 5.7GHz", categoria_id=5, imagen_url="https://placehold.co/400x300?text=Ryzen+9", activo=True),
        ]
        for p in productos:
            session.add(p)

        admin = Admin(username="admin", password_hash=hash_password("admin123"))
        session.add(admin)
        session.commit()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# ── App ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_data()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Endpoints Públicos ──────────────────────────────────
@app.get("/api/categorias", response_model=list[CategoriaOut])
def listar_categorias(session: SessionDep):
    return session.exec(select(Categoria)).all()


@app.get("/api/productos", response_model=list[ProductoOut])
def listar_productos(
    session: SessionDep,
    categoria_id: int | None = Query(default=None),
    solo_activos: bool = Query(default=True),
):
    query = select(Producto)
    if solo_activos:
        query = query.where(Producto.activo == True)
    if categoria_id:
        query = query.where(Producto.categoria_id == categoria_id)
    productos = session.exec(query).all()
    result = []
    for p in productos:
        cat = session.get(Categoria, p.categoria_id)
        result.append(ProductoOut(
            id=p.id, nombre=p.nombre, precio=p.precio,
            descripcion=p.descripcion, categoria_id=p.categoria_id,
            categoria_nombre=cat.nombre if cat else None,
            imagen_url=p.imagen_url, activo=p.activo,
        ))
    return result


@app.get("/api/producto", response_model=ProductoOut)
def obtener_producto(session: SessionDep, id: int = Query(...)):
    p = session.get(Producto, id)
    if not p or not p.activo:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    cat = session.get(Categoria, p.categoria_id)
    return ProductoOut(
        id=p.id, nombre=p.nombre, precio=p.precio,
        descripcion=p.descripcion, categoria_id=p.categoria_id,
        categoria_nombre=cat.nombre if cat else None,
        imagen_url=p.imagen_url, activo=p.activo,
    )


# ── Auth ─────────────────────────────────────────────────
@app.post("/api/auth")
def login(body: LoginRequest, session: SessionDep):
    admin = session.exec(select(Admin).where(Admin.username == body.username)).first()
    if not admin or admin.password_hash != hash_password(body.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"id": admin.id, "username": admin.username, "token": ADMIN_TOKEN}


def verify_admin(authorization: str | None = Header(default=None)):
    if not authorization or authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")
    return True


# ── Endpoints Admin ────────────────────────────────────
@app.post("/api/admin/productos", response_model=ProductoOut)
def crear_producto(body: ProductoCreate, session: SessionDep, auth: bool = Depends(verify_admin)):
    if body.categoria_id:
        cat = session.get(Categoria, body.categoria_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Categoría no existe")
    producto = Producto(
        nombre=body.nombre, precio=body.precio,
        descripcion=body.descripcion, categoria_id=body.categoria_id,
        imagen_url=body.imagen_url,
    )
    session.add(producto)
    session.commit()
    session.refresh(producto)
    cat = session.get(Categoria, producto.categoria_id)
    return ProductoOut(
        id=producto.id, nombre=producto.nombre, precio=producto.precio,
        descripcion=producto.descripcion, categoria_id=producto.categoria_id,
        categoria_nombre=cat.nombre if cat else None,
        imagen_url=producto.imagen_url, activo=producto.activo,
    )


@app.put("/api/admin/productos/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, body: ProductoUpdate, session: SessionDep, auth: bool = Depends(verify_admin)):
    producto = session.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if body.nombre is not None:
        producto.nombre = body.nombre
    if body.precio is not None:
        producto.precio = body.precio
    if body.descripcion is not None:
        producto.descripcion = body.descripcion
    if body.categoria_id is not None:
        cat = session.get(Categoria, body.categoria_id)
        if not cat:
            raise HTTPException(status_code=400, detail="Categoría no existe")
        producto.categoria_id = body.categoria_id
    if body.imagen_url is not None:
        producto.imagen_url = body.imagen_url
    if body.activo is not None:
        producto.activo = body.activo
    session.add(producto)
    session.commit()
    session.refresh(producto)
    cat = session.get(Categoria, producto.categoria_id)
    return ProductoOut(
        id=producto.id, nombre=producto.nombre, precio=producto.precio,
        descripcion=producto.descripcion, categoria_id=producto.categoria_id,
        categoria_nombre=cat.nombre if cat else None,
        imagen_url=producto.imagen_url, activo=producto.activo,
    )
