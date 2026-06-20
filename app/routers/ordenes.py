from fastapi import APIRouter, HTTPException
from app.database import get_pool
from app.schemas import OrdenCreate, OrdenUpdate, OrdenOut, OrdenItemOut

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


async def _build_orden_out(pool, orden_id: int) -> dict:
    orden = await pool.fetchrow("SELECT * FROM ordenes WHERE id=$1", orden_id)
    if not orden:
        return None
    items = await pool.fetch(
        "SELECT * FROM orden_items WHERE orden_id=$1", orden_id
    )
    result = dict(orden)
    result["items"] = [dict(i) for i in items]
    return result


@router.get("/", response_model=list[OrdenOut])
async def listar_ordenes(cliente_id: int | None = None, estado: str | None = None):
    pool = await get_pool()
    query = "SELECT id FROM ordenes WHERE 1=1"
    params: list = []
    i = 1
    if cliente_id:
        query += f" AND cliente_id=${i}"; params.append(cliente_id); i += 1
    if estado:
        query += f" AND estado=${i}"; params.append(estado)
    query += " ORDER BY id DESC"
    ids = await pool.fetch(query, *params)
    return [await _build_orden_out(pool, r["id"]) for r in ids]


@router.get("/{id}", response_model=OrdenOut)
async def obtener_orden(id: int):
    pool = await get_pool()
    orden = await _build_orden_out(pool, id)
    if not orden:
        raise HTTPException(404, "Orden no encontrada")
    return orden


@router.post("/", response_model=OrdenOut, status_code=201)
async def crear_orden(data: OrdenCreate):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Validar cliente
            cliente = await conn.fetchrow(
                "SELECT id FROM clientes WHERE id=$1", data.cliente_id
            )
            if not cliente:
                raise HTTPException(404, "Cliente no encontrado")

            # Crear orden
            orden = await conn.fetchrow(
                "INSERT INTO ordenes (cliente_id) VALUES ($1) RETURNING *",
                data.cliente_id,
            )
            orden_id = orden["id"]

            # Insertar items
            for item in data.items:
                producto = await conn.fetchrow(
                    "SELECT precio, stock FROM productos WHERE id=$1 AND activo=TRUE",
                    item.producto_id,
                )
                if not producto:
                    raise HTTPException(
                        404, f"Producto {item.producto_id} no disponible"
                    )
                if producto["stock"] < item.cantidad:
                    raise HTTPException(
                        400,
                        f"Stock insuficiente para producto {item.producto_id} "
                        f"(disponible: {producto['stock']})",
                    )
                await conn.execute(
                    """INSERT INTO orden_items (orden_id, producto_id, cantidad, precio_unit)
                       VALUES ($1,$2,$3,$4)""",
                    orden_id, item.producto_id, item.cantidad, producto["precio"],
                )
                # Descontar stock
                await conn.execute(
                    "UPDATE productos SET stock=stock-$1 WHERE id=$2",
                    item.cantidad, item.producto_id,
                )

    return await _build_orden_out(pool, orden_id)


@router.patch("/{id}/estado", response_model=OrdenOut)
async def cambiar_estado(id: int, data: OrdenUpdate):
    pool = await get_pool()
    row = await pool.fetchrow(
        "UPDATE ordenes SET estado=$2 WHERE id=$1 RETURNING *", id, data.estado
    )
    if not row:
        raise HTTPException(404, "Orden no encontrada")
    return await _build_orden_out(pool, id)


@router.delete("/{id}", status_code=204)
async def cancelar_orden(id: int):
    """Cancela y restaura stock."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            orden = await conn.fetchrow(
                "SELECT estado FROM ordenes WHERE id=$1", id
            )
            if not orden:
                raise HTTPException(404, "Orden no encontrada")
            if orden["estado"] in ("entregada", "cancelada"):
                raise HTTPException(400, f"No se puede cancelar en estado '{orden['estado']}'")

            items = await conn.fetch(
                "SELECT producto_id, cantidad FROM orden_items WHERE orden_id=$1", id
            )
            for item in items:
                await conn.execute(
                    "UPDATE productos SET stock=stock+$1 WHERE id=$2",
                    item["cantidad"], item["producto_id"],
                )
            await conn.execute(
                "UPDATE ordenes SET estado='cancelada' WHERE id=$1", id
            )
