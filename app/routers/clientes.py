from fastapi import APIRouter, HTTPException
from app.database import get_pool
from app.schemas import ClienteCreate, ClienteUpdate, ClienteOut

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=list[ClienteOut])
async def listar_clientes():
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM clientes ORDER BY id")
    return [dict(r) for r in rows]


@router.get("/{id}", response_model=ClienteOut)
async def obtener_cliente(id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM clientes WHERE id=$1", id)
    if not row:
        raise HTTPException(404, "Cliente no encontrado")
    return dict(row)


@router.post("/", response_model=ClienteOut, status_code=201)
async def crear_cliente(data: ClienteCreate):
    pool = await get_pool()
    try:
        row = await pool.fetchrow(
            """INSERT INTO clientes (nombre, email, telefono, direccion)
               VALUES ($1,$2,$3,$4) RETURNING *""",
            data.nombre, data.email, data.telefono, data.direccion,
        )
    except Exception as e:
        raise HTTPException(400, f"Error al crear cliente: {e}")
    return dict(row)


@router.patch("/{id}", response_model=ClienteOut)
async def actualizar_cliente(id: int, data: ClienteUpdate):
    pool = await get_pool()
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(400, "Sin campos para actualizar")
    sets = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    values = list(fields.values())
    row = await pool.fetchrow(
        f"UPDATE clientes SET {sets} WHERE id=$1 RETURNING *", id, *values
    )
    if not row:
        raise HTTPException(404, "Cliente no encontrado")
    return dict(row)


@router.delete("/{id}", status_code=204)
async def eliminar_cliente(id: int):
    pool = await get_pool()
    result = await pool.execute("DELETE FROM clientes WHERE id=$1", id)
    if result == "DELETE 0":
        raise HTTPException(404, "Cliente no encontrado")
