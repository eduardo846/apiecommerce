from fastapi import APIRouter, HTTPException
from app.database import get_pool
from app.schemas import CategoriaCreate, CategoriaUpdate, CategoriaOut

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("/", response_model=list[CategoriaOut])
async def listar_categorias():
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM categorias ORDER BY nombre")
    return [dict(r) for r in rows]


@router.get("/{id}", response_model=CategoriaOut)
async def obtener_categoria(id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM categorias WHERE id=$1", id)
    if not row:
        raise HTTPException(404, "Categoría no encontrada")
    return dict(row)


@router.post("/", response_model=CategoriaOut, status_code=201)
async def crear_categoria(data: CategoriaCreate):
    pool = await get_pool()
    try:
        row = await pool.fetchrow(
            "INSERT INTO categorias (nombre, descripcion) VALUES ($1,$2) RETURNING *",
            data.nombre, data.descripcion,
        )
    except Exception as e:
        raise HTTPException(400, f"Error: {e}")
    return dict(row)


@router.patch("/{id}", response_model=CategoriaOut)
async def actualizar_categoria(id: int, data: CategoriaUpdate):
    pool = await get_pool()
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(400, "Sin campos")
    sets = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    row = await pool.fetchrow(
        f"UPDATE categorias SET {sets} WHERE id=$1 RETURNING *", id, *fields.values()
    )
    if not row:
        raise HTTPException(404, "Categoría no encontrada")
    return dict(row)


@router.delete("/{id}", status_code=204)
async def eliminar_categoria(id: int):
    pool = await get_pool()
    result = await pool.execute("DELETE FROM categorias WHERE id=$1", id)
    if result == "DELETE 0":
        raise HTTPException(404, "Categoría no encontrada")
