from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import get_pool, close_pool
from app.routers import clientes, productos, ordenes, categorias


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()          # inicializar pool al arrancar
    yield
    await close_pool()        # cerrar al apagar


app = FastAPI(
    title="E-Commerce API",
    description="CRUD completo: Clientes, Productos, Órdenes, Categorías",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(ordenes.router)
app.include_router(categorias.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "docs": "/docs"}
