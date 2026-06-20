# E-Commerce API — FastAPI + PostgreSQL

## Estructura

```
ecommerce-api/
├── schema.sql              # Schema PostgreSQL + datos de prueba
├── requirements.txt
├── .env                    # Configurar DATABASE_URL aquí
└── app/
    ├── main.py             # Entry point FastAPI
    ├── database.py         # Pool asyncpg
    ├── schemas.py          # Modelos Pydantic
    └── routers/
        ├── clientes.py
        ├── productos.py
        ├── ordenes.py
        └── categorias.py
```

## Setup rápido

### 1. Crear la base de datos en PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE ecommerce_db;"
psql -U postgres -d ecommerce_db -f schema.sql
```

### 2. Configurar `.env`

```env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/ecommerce_db
```

### 3. Instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 4. Arrancar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

---

## Endpoints

### Clientes
| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | /clientes | Listar todos |
| GET    | /clientes/{id} | Obtener uno |
| POST   | /clientes | Crear |
| PATCH  | /clientes/{id} | Actualizar parcial |
| DELETE | /clientes/{id} | Eliminar |

### Productos
| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | /productos?activo=true&search=auricular | Listar con filtros |
| GET    | /productos/{id} | Obtener uno |
| POST   | /productos | Crear |
| PATCH  | /productos/{id} | Actualizar parcial |
| DELETE | /productos/{id} | Eliminar |

### Órdenes
| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | /ordenes?cliente_id=1 | Listar |
| GET    | /ordenes/{id} | Obtener con items |
| POST   | /ordenes | Crear (descuenta stock) |
| PATCH  | /ordenes/{id}/estado | Cambiar estado |
| DELETE | /ordenes/{id} | Cancelar (restaura stock) |

### Categorías
| Método | URL | Descripción |
|--------|-----|-------------|
| GET    | /categorias | Listar |
| POST   | /categorias | Crear |
| PATCH  | /categorias/{id} | Actualizar |
| DELETE | /categorias/{id} | Eliminar |

---

## Ejemplo: crear una orden

```json
POST /ordenes
{
  "cliente_id": 1,
  "items": [
    { "producto_id": 1, "cantidad": 2 },
    { "producto_id": 3, "cantidad": 1 }
  ]
}
```

La API valida stock, descuenta automáticamente, y calcula el total vía trigger SQL.
