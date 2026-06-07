# TechStore — Tienda Virtual de Productos Tecnológicos

## Resumen ejecutivo

TechStore es una aplicación web full-stack para la gestión y venta de productos tecnológicos. Construida con FastAPI en el backend y HTML/CSS/JavaScript vanilla en el frontend, permite a los visitantes navegar un catálogo de productos filtrado por categorías, y a los administradores gestionar el inventario mediante un panel protegido con autenticación. La base de datos corre sobre PostgreSQL en producción (desplegada en Supabase) y la aplicación se despliega en Render.

El repositorio original era un chat con inteligencia artificial (Gemini) desarrollado como proyecto educativo. Fue transformado completamente a una tienda virtual, reemplazando modelos, endpoints, frontend, tests y toda la lógica de negocio.

---

## 1. Cambios realizados respecto a la versión inicial

### Archivos agregados

| Archivo | Descripción |
|---------|-------------|
| `static/admin.html` | Panel de administración con login, dashboard y modal CRUD |
| `static/admin.js` | Lógica del panel admin: autenticación, CRUD, toggle activo |
| `tests/unit/test_tienda.py` | 12 tests para los endpoints de la tienda |
| `migrations/versions/0001_create_tienda_tables.py` | Migración inicial con tablas `categorias`, `productos`, `admins` |
| `.env.example` | Plantilla de variables de entorno para nuevos desarrolladores |

### Archivos eliminados

| Archivo | Motivo |
|---------|--------|
| `tests/unit/test_chat.py` | Tests del chat con Gemini (ya no aplican) |
| `tests/e2e/test_e2e.py` | Tests E2E con Playwright (ya no aplican) |
| `tests/e2e/mi-test.spec.ts` | Spec de Playwright (ya no aplica) |
| `tests/e2e/__init__.py` | Init del paquete E2E |
| `migrations/versions/7d6e22c636b0_*.py` | Migración del modelo de chat (tabla usuarios) |
| `migrations/versions/99c5e79318f8_*.py` | Migración de login/register del chat |

### Archivos modificados

| Archivo | Cambio principal |
|---------|------------------|
| `main.py` | Reescribido completamente: nuevos modelos (`Categoria`, `Producto`, `Admin`), nuevos endpoints, seed data, autenticación por token |
| `static/index.html` | De interfaz de chat a catálogo de productos con grid y filtros |
| `static/app.js` | De lógica de chat a fetching de productos, renderizado y filtrado |
| `tests/conftest.py` | Fixtures actualizadas para los nuevos modelos y seed data de tienda |
| `requirements.txt` | Reducido de 85 a 11 dependencias (eliminados `google-genai`, `playwright`, etc.) |
| `.github/workflows/ci.yml` | Simplificado de 5 jobs a 1 job que corre `pytest` |
| `alembic.ini` | Actualizada URL de base de datos de ejemplo |
| `README.md` | Documentación actualizada para la tienda (este archivo) |
| `.gitignore` | Agregados `venv/`, `*.db`, `test-results/`, `.pytest_cache/` |

---

## 2. Arquitectura final del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      Navegador Web                           │
│   ┌──────────────────────┐   ┌──────────────────────────┐   │
│   │  / (index.html)       │   │  /static/admin.html      │   │
│   │  Catálogo público     │   │  Panel de administración │   │
│   │  app.js               │   │  admin.js                │   │
│   └──────────┬───────────┘   └───────────┬──────────────┘   │
│              │                            │                  │
└──────────────┼────────────────────────────┼──────────────────┘
               │                            │
               │     HTTP / API REST        │
               ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                         │
│                                                              │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │ Endpoints   │  │  SQLModel    │  │  Autenticación   │  │
│   │ públicos    │  │  (ORM)       │  │  Bearer Token    │  │
│   │ /api/*      │  │              │  │  /api/auth       │  │
│   └──────┬──────┘  └──────┬───────┘  └──────────────────┘  │
│          │                │                                  │
└──────────┼────────────────┼──────────────────────────────────┘
           │                │
           ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL / Supabase                           │
│                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │  categorias  │  │  productos   │  │     admins       │  │
│   │  id          │  │  id          │  │  id              │  │
│   │  nombre (PK) │──│  categoria_id│  │  username (PK)   │  │
│   └──────────────┘  │  nombre      │  │  password_hash   │  │
│                     │  precio      │  └──────────────────┘  │
│                     │  descripcion │                         │
│                     │  imagen_url  │                         │
│                     │  activo      │                         │
│                     │  created_at  │                         │
│                     └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

**Flujo de datos:**

1. **Catálogo público:** El navegador carga `index.html` → `app.js` hace `fetch()` a `GET /api/productos` y `GET /api/categorias` → FastAPI consulta PostgreSQL → devuelve JSON → JS renderiza tarjetas de productos con filtro por categoría.

2. **Panel admin:** El navegador carga `admin.html` → `admin.js` muestra formulario de login → `POST /api/auth` valida credenciales contra tabla `admins` → devuelve token Bearer → JS guarda token en `localStorage` → carga productos con `GET /api/productos?solo_activos=false` → CRUD mediante `POST`/`PUT` a `/api/admin/productos` con token en header.

---

## 3. Tecnologías utilizadas

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| Backend | **FastAPI** | 0.132.0 | Framework web asíncrono para la API REST |
| Backend | **Uvicorn** | 0.41.0 | Servidor ASGI para servir la aplicación |
| ORM | **SQLModel** | 0.0.37 | ORM basado en SQLAlchemy + Pydantic |
| ORM | **SQLAlchemy** | 2.0.48 | Motor de base de datos subyacente |
| DB | **PostgreSQL** | 16 | Base de datos relacional en producción |
| DB | **Supabase** | — | PostgreSQL administrado en la nube |
| Migraciones | **Alembic** | 1.18.4 | Control de versiones del esquema de BD |
| Cliente DB | **psycopg2-binary** | 2.9.11 | Driver PostgreSQL para Python |
| Validación | **Pydantic** | 2.12.5 | Validación de datos y schemas |
| Env vars | **python-dotenv** | 1.2.1 | Carga de variables de entorno desde `.env` |
| Testing | **pytest** | 9.0.3 | Framework de tests |
| Testing | **httpx** | 0.28.1 | Cliente HTTP para TestClient |
| CI/CD | **GitHub Actions** | — | Pipeline de integración continua |
| Deploy | **Render** | — | Plataforma cloud para hosting |
| Frontend | **HTML5 + CSS3** | — | Interfaz de usuario (vanilla, sin frameworks) |
| Frontend | **JavaScript** | ES2020 | Lógica del cliente (fetch, DOM, localStorage) |

---

## 4. Instrucciones de instalación local

### Requisitos previos

- Python 3.12+
- PostgreSQL 16 (o Docker)
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/tienda-tecnologica.git
cd tienda-tecnologica

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales (ver sección 5)

# 5. Iniciar PostgreSQL (con Docker)
docker run --name tienda-db \
  -e POSTGRES_USER=tienda_user \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=tiendadb \
  -p 5432:5432 \
  -d postgres:16

# 6. Aplicar migraciones (opcional, create_all corre en startup)
alembic upgrade head

# 7. Iniciar servidor de desarrollo
uvicorn main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`.

---

## 5. Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```bash
# .env
DATABASE_URL=postgresql://usuario:password@host:5432/postgres
ADMIN_TOKEN=token-seguro-para-admin
```

| Variable | Obligatoria | Descripción | Ejemplo |
|----------|-------------|-------------|---------|
| `DATABASE_URL` | Sí | Cadena de conexión a PostgreSQL | `postgresql://user:pass@localhost:5432/tiendadb` |
| `ADMIN_TOKEN` | No | Token Bearer para autenticación admin (default: `admin-token-seguro`) | `mi-token-secreto` |

> **Importante:** El archivo `.env` contiene credenciales reales. NO debe subirse al repositorio (está en `.gitignore`).

---

## 6. Despliegue

### En Render

1. Crear un **Web Service** en [Render](https://render.com) conectando el repositorio de GitHub.
2. Crear una base de datos **PostgreSQL Free** desde el dashboard de Render.
3. En la configuración del Web Service, agregar:
   - `Build Command`: `pip install -r requirements.txt`
   - `Start Command`: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Agregar variables de entorno en Render:
   - `DATABASE_URL`: La URL interna de la base de datos de Render.
   - `ADMIN_TOKEN`: Token seguro para el panel admin.
5. Hacer deploy. Render instala dependencias, inicia el servidor y la app crea las tablas automáticamente al arrancar.

### En Supabase (base de datos)

1. Crear un proyecto en [Supabase](https://supabase.com) (plan Free).
2. Obtener la **Connection string** desde Project Settings → Database → URI.
3. Usar esa URI como `DATABASE_URL` en el `.env` o en las variables de entorno de Render.

---

## 7. Endpoints de la API

| Método | Endpoint | Autenticación | Descripción | Parámetros |
|--------|----------|---------------|-------------|------------|
| `GET` | `/` | No | Sirve el frontend del catálogo | — |
| `GET` | `/health` | No | Health check | — |
| `GET` | `/api/categorias` | No | Lista todas las categorías | — |
| `GET` | `/api/productos` | No | Lista productos activos | `?categoria_id=N` (opcional), `?solo_activos=true` (default) |
| `GET` | `/api/producto` | No | Obtiene un producto por ID | `?id=N` (requerido) |
| `POST` | `/api/auth` | No | Login de administrador | `{"username": "...", "password": "..."}` |
| `POST` | `/api/admin/productos` | Bearer Token | Crea un nuevo producto | `{"nombre", "precio", "descripcion", "categoria_id", "imagen_url"}` |
| `PUT` | `/api/admin/productos/{id}` | Bearer Token | Actualiza un producto (parcial) | `{"precio": 199.99, "activo": false}` |

### Admin por defecto (seed data)

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> Al iniciar la app por primera vez, se seedan automáticamente 5 categorías, 10 productos de ejemplo y el usuario admin.

---

## 8. Tests

Los tests usan SQLite en memoria, no requieren PostgreSQL ni credenciales.

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest --cov=main tests/
```

### Tests existentes (12)

| Test | Endpoint | Escenario |
|------|----------|-----------|
| `test_listar_categorias` | `GET /api/categorias` | Listar categorías devuelve datos |
| `test_listar_productos` | `GET /api/productos` | Listar productos devuelve array |
| `test_productos_por_categoria` | `GET /api/productos?categoria_id=1` | Filtro por categoría funciona |
| `test_obtener_producto_por_id` | `GET /api/producto?id=1` | Obtener producto existente |
| `test_producto_no_existe` | `GET /api/producto?id=99999` | Producto inexistente → 404 |
| `test_login_admin_correcto` | `POST /api/auth` | Login con credenciales correctas |
| `test_login_admin_incorrecto` | `POST /api/auth` | Login con password incorrecta → 401 |
| `test_crear_producto_admin` | `POST /api/admin/productos` | Crear producto autenticado |
| `test_crear_producto_sin_auth` | `POST /api/admin/productos` | Crear producto sin auth → 401 |
| `test_actualizar_producto` | `PUT /api/admin/productos/1` | Actualizar precio |
| `test_desactivar_producto` | `PUT /api/admin/productos/1` | Desactivar producto |
| `test_producto_inactivo_no_en_catalogo` | `GET /api/productos` | Producto inactivo no aparece |

---

## 9. Sustentación técnica

### ¿Por qué FastAPI?

- **Rendimiento:** Es uno de los frameworks Python más rápidos gracias a Starlette y async.
- **Tipado:** Validación automática con Pydantic; los schemas duplican como documentación.
- **Documentación automática:** Genera Swagger UI en `/docs` sin configuración adicional.
- **Inyección de dependencias:** Sistema nativo que facilita el testing (override de dependencias en tests).
- **Python moderno:** Aprovecha type hints de Python 3.12 (`int | None`, `Annotated`).

### ¿Por qué PostgreSQL?

- **Madurez:** Base de datos relacional más robusta del ecosistema open-source.
- **SQL estándar:** Consultas, joins, índices, restricciones de integridad referencial.
- **Tipos de datos:** Soporte nativo para booleanos, fechas con timezone, floats precisos.
- **Escalabilidad:** Maneja desde desarrollo local hasta producción con millones de registros.
- **Ecosistema:** Integración nativa con Supabase, Render, Alembic y SQLAlchemy.

### ¿Por qué Supabase?

- **PostgreSQL administrado:** Ofrece una base de datos PostgreSQL gratis sin necesidad de administrar servidores.
- **Pooler automático:** El connection pooler (`pooler.supabase.com`) maneja conexiones concurrentes sin saturar la base de datos.
- **Capa gratuita generosa:** 500 MB de almacenamiento, suficientes para aplicaciones en etapas tempranas.
- **Integración simple:** Solo se necesita la URI de conexión como `DATABASE_URL`; no requiere SDK ni configuración especial.
- **Dashboard visual:** Permite explorar datos, ejecutar consultas SQL y monitorear rendimiento desde el navegador.

### ¿Por qué Render?

- **Deploy sencillo:** Conecta el repositorio de GitHub y Render detecta automáticamente el entorno Python.
- **PostgreSQL integrado:** Ofrece bases de datos PostgreSQL como servicio adicional.
- **Capa gratuita:** El plan Free incluye 750 horas/mes de computo y PostgreSQL con 1 GB de almacenamiento.
- **SSL automático:** Provee certificados HTTPS sin configuración.
- **Cero mantenimiento:** Los deploys se disparan con cada push a main; la plataforma maneja actualizaciones de seguridad.

### ¿Cómo se comunica el frontend con el backend?

La comunicación es mediante **API REST** sobre **HTTP**, sin frameworks frontend intermediarios:

1. **Arquitectura SPA (Single Page Application):** Cada página HTML (`index.html`, `admin.html`) carga un archivo JavaScript que gestiona la interfaz.

2. **Fetch API nativa:** El JS usa `fetch()` para realizar peticiones HTTP a los endpoints de FastAPI. No hay librerías externas (ni Axios, ni jQuery).

3. **Formato JSON:** Tanto las peticiones (request body) como las respuestas (response body) utilizan JSON. FastAPI serializa/deserializa automáticamente usando Pydantic.

4. **Autenticación vía Header:** El admin panel obtiene un token Bearer mediante `POST /api/auth`, lo almacena en `localStorage`, y lo envía en cada petición a los endpoints protegidos mediante el header `Authorization: Bearer <token>`.

5. **CORS abierto:** El middleware CORS de FastAPI permite peticiones desde cualquier origen (`allow_origins=["*"]`), necesario porque el frontend estático y la API pueden servirse desde el mismo dominio o desde dominios distintos en desarrollo.

6. **Servicio de archivos estáticos:** FastAPI monta la carpeta `static/` mediante `StaticFiles`, sirviendo HTML, CSS y JS directamente. El endpoint raíz `GET /` redirige a `static/index.html`.

---

## Estructura del proyecto

```
tienda-tecnologica/
├── main.py                       # Aplicación FastAPI (modelos, endpoints, seed)
├── requirements.txt              # Dependencias del proyecto
├── alembic.ini                   # Configuración de Alembic
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore                    # Archivos ignorados por git
├── README.md                     # Documentación (este archivo)
├── AGENTS.md                     # Instrucciones para asistentes IA (legacy)
├── GUIA.md                       # Guía educativa original (legacy del chat)
├── migrations/
│   ├── env.py                    # Configuración del entorno Alembic
│   ├── script.py.mako            # Template para nuevas migraciones
│   └── versions/
│       └── 0001_create_tienda_tables.py   # Migración inicial
├── static/
│   ├── index.html                # Catálogo público de productos
│   ├── admin.html                # Panel de administración
│   ├── app.js                    # JavaScript del catálogo público
│   └── admin.js                  # JavaScript del panel admin
├── tests/
│   ├── conftest.py               # Fixtures de pytest
│   └── unit/
│       └── test_tienda.py        # 12 tests de endpoints
└── .github/workflows/
    └── ci.yml                    # Pipeline de integración continua
```

---

## Licencia

Proyecto educativo. Sin licencia específica.
