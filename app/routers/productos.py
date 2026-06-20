from fastapi import APIRouter, HTTPException, Query
from app.database import get_pool
from app.schemas import ProductoCreate, ProductoUpdate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoOut])
async def listar_productos(
    activo: bool | None = None,
    categoria_id: int | None = None,
    search: str | None = Query(None, description="Buscar por nombre"),
):
    pool = await get_pool()
    query = "SELECT * FROM productos WHERE 1=1"
    params: list = []
    i = 1
    if activo is not None:
        query += f" AND activo=${i}"; params.append(activo); i += 1
    if categoria_id is not None:
        query += f" AND categoria_id=${i}"; params.append(categoria_id); i += 1
    if search:
        query += f" AND nombre ILIKE ${i}"; params.append(f"%{search}%"); i += 1
    query += " ORDER BY id"
    rows = await pool.fetch(query, *params)
    return [dict(r) for r in rows]


@router.get("/{id}", response_model=ProductoOut)
async def obtener_producto(id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM productos WHERE id=$1", id)
    if not row:
        raise HTTPException(404, "Producto no encontrado")
    return dict(row)


@router.post("/", response_model=ProductoOut, status_code=201)
async def crear_producto(data: ProductoCreate):
    pool = await get_pool()
    row = await pool.fetchrow(
        """INSERT INTO productos (nombre, descripcion, precio, stock, categoria_id, activo)
           VALUES ($1,$2,$3,$4,$5,$6) RETURNING *""",
        data.nombre, data.descripcion, data.precio,
        data.stock, data.categoria_id, data.activo,
    )
    return dict(row)


@router.patch("/{id}", response_model=ProductoOut)
async def actualizar_producto(id: int, data: ProductoUpdate):
    pool = await get_pool()
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(400, "Sin campos para actualizar")
    sets = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    row = await pool.fetchrow(
        f"UPDATE productos SET {sets} WHERE id=$1 RETURNING *", id, *fields.values()
    )
    if not row:
        raise HTTPException(404, "Producto no encontrado")
    return dict(row)


@router.delete("/{id}", status_code=204)
async def eliminar_producto(id: int):
    pool = await get_pool()
    result = await pool.execute("DELETE FROM productos WHERE id=$1", id)
    if result == "DELETE 0":
        raise HTTPException(404, "Producto no encontrado")
