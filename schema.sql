-- ============================================================
-- E-COMMERCE SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS clientes (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    telefono    VARCHAR(20),
    direccion   TEXT,
    creado_en   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categorias (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(80) UNIQUE NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id           SERIAL PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    descripcion  TEXT,
    precio       NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    stock        INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    activo       BOOLEAN DEFAULT TRUE,
    creado_en    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ordenes (
    id          SERIAL PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    estado      VARCHAR(30) NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente','pagada','enviada','entregada','cancelada')),
    total       NUMERIC(12, 2) DEFAULT 0,
    creado_en   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orden_items (
    id          SERIAL PRIMARY KEY,
    orden_id    INTEGER NOT NULL REFERENCES ordenes(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unit NUMERIC(10, 2) NOT NULL
);

-- Recalcular total al insertar/borrar items
CREATE OR REPLACE FUNCTION actualizar_total_orden()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    UPDATE ordenes
    SET total = (
        SELECT COALESCE(SUM(cantidad * precio_unit), 0)
        FROM orden_items WHERE orden_id = COALESCE(NEW.orden_id, OLD.orden_id)
    )
    WHERE id = COALESCE(NEW.orden_id, OLD.orden_id);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_total_insert
AFTER INSERT OR UPDATE ON orden_items
FOR EACH ROW EXECUTE FUNCTION actualizar_total_orden();

CREATE TRIGGER trg_total_delete
AFTER DELETE ON orden_items
FOR EACH ROW EXECUTE FUNCTION actualizar_total_orden();

-- ---- Datos de prueba ----
INSERT INTO categorias (nombre, descripcion) VALUES
    ('Electrónica',  'Gadgets y dispositivos'),
    ('Ropa',         'Prendas de vestir'),
    ('Alimentos',    'Productos comestibles')
ON CONFLICT DO NOTHING;

INSERT INTO clientes (nombre, email, telefono, direccion) VALUES
    ('Ana García',   'ana@example.com',   '3001234567', 'Calle 10 #5-20, Bogotá'),
    ('Luis Pérez',   'luis@example.com',  '3109876543', 'Av. 45 #12-30, Medellín')
ON CONFLICT DO NOTHING;

INSERT INTO productos (nombre, precio, stock, categoria_id) VALUES
    ('Auriculares Bluetooth', 89900,  50, 1),
    ('Camiseta Polo',         35000, 200, 2),
    ('Café Molido 500g',       18500, 100, 3)
ON CONFLICT DO NOTHING;
