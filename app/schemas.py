from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Categorias ──────────────────────────────────────────────
class CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=80)
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase): pass
class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
class CategoriaOut(CategoriaBase):
    id: int


# ── Clientes ─────────────────────────────────────────────────
class ClienteBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteCreate(ClienteBase): pass
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
class ClienteOut(ClienteBase):
    id: int
    creado_en: datetime


# ── Productos ────────────────────────────────────────────────
class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    precio: float = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    categoria_id: Optional[int] = None
    activo: bool = True

class ProductoCreate(ProductoBase): pass
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria_id: Optional[int] = None
    activo: Optional[bool] = None
class ProductoOut(ProductoBase):
    id: int
    creado_en: datetime


# ── Ordenes ──────────────────────────────────────────────────
class OrdenItemIn(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)

class OrdenCreate(BaseModel):
    cliente_id: int
    items: list[OrdenItemIn] = Field(..., min_length=1)

class OrdenUpdate(BaseModel):
    estado: str = Field(..., pattern="^(pendiente|pagada|enviada|entregada|cancelada)$")

class OrdenItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unit: float

class OrdenOut(BaseModel):
    id: int
    cliente_id: int
    estado: str
    total: float
    creado_en: datetime
    items: list[OrdenItemOut] = []
