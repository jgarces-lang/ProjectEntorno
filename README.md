# TechStore — Tienda Virtual de Productos Tecnológicos

Aplicación web de tienda virtual construida con **FastAPI**, **SQLAlchemy (SQLModel)**, **PostgreSQL** y frontend vanilla HTML/CSS/JS.

## Características

- Catálogo público de productos con filtro por categorías
- Panel de administración con login
- CRUD completo de productos (crear, editar, activar/desactivar)
- API REST documentada
- Migraciones con Alembic
- Tests automatizados con pytest
- CI pipeline con GitHub Actions

## Stack

| Componente | Tecnología |
|------------|-----------|
| Backend | FastAPI (Python 3.12) |
| Base de datos | PostgreSQL + SQLAlchemy (SQLModel) |
| Migraciones | Alembic |
| Frontend | HTML, CSS, JavaScript vanilla |
| Testing | pytest + httpx (TestClient) |
| CI/CD | GitHub Actions |

## Requisitos

- Python 3.12+
- PostgreSQL (o Docker)
- pip

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/tienda-tecnologica.git
cd tienda-tecnologica

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración
```

## Base de datos

### Con Docker (recomendado para desarrollo)

```bash
docker run --name tienda-db \
  -e POSTGRES_USER=tienda_user \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=tiendadb \
  -p 5432:5432 \
  -d postgres:16
```

### Sin Docker

Asegurate de tener PostgreSQL corriendo y crear la base de datos:

```bash
createdb tiendadb
```

### Configurar `.env`

```
DATABASE_URL=postgresql://tienda_user:secret@localhost:5432/tiendadb
ADMIN_TOKEN=admin-token-seguro-cambiar-en-produccion
```

## Ejecutar

```bash
# Iniciar servidor de desarrollo
uvicorn main:app --reload
```

La app arranca en `http://localhost:8000`.

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Catálogo público |
| GET | `/health` | Health check |
| GET | `/api/categorias` | Listar categorías |
| GET | `/api/productos` | Listar productos activos |
| GET | `/api/producto?id=N` | Obtener producto por ID |
| POST | `/api/auth` | Login de administrador |
| POST | `/api/admin/productos` | Crear producto (admin) |
| PUT | `/api/admin/productos/{id}` | Actualizar producto (admin) |

### Admin por defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

El panel admin está en `/static/admin.html`.

## Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest --cov=main tests/
```

## Migraciones (Alembic)

```bash
# Aplicar migraciones
alembic upgrade head

# Crear nueva migración (después de cambiar modelos)
alembic revision --autogenerate -m "descripcion"
```

## Despliegue en Render

1. Crear un **Web Service** en Render conectado al repositorio
2. Agregar una base de datos **PostgreSQL Free** en Render
3. Configurar variables de entorno en Render:
   - `DATABASE_URL`: La URL de la base de datos de Render
   - `ADMIN_TOKEN`: Un token seguro para el panel admin
4. Render ejecutará automáticamente `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Estructura del proyecto

```
.
├── main.py                 # Aplicación FastAPI (modelos, endpoints)
├── requirements.txt        # Dependencias
├── alembic.ini             # Configuración de Alembic
├── .env.example            # Variables de entorno de ejemplo
├── .gitignore
├── README.md
├── migrations/
│   ├── env.py              # Entorno de Alembic
│   └── versions/           # Migraciones
├── static/
│   ├── index.html          # Catálogo público
│   ├── admin.html          # Panel de administración
│   ├── app.js              # JS del catálogo
│   └── admin.js            # JS del panel admin
├── tests/
│   ├── conftest.py         # Fixtures de pytest
│   ├── unit/
│   │   └── test_tienda.py  # Tests de endpoints
│   └── e2e/                # Tests end-to-end
└── .github/workflows/
    └── ci.yml              # GitHub Actions
```
