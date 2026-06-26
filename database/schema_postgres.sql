-- ============================================
-- SCHEMA: Finanzas Personales (PostgreSQL / Supabase)
-- Ejecuta este script en: Supabase → SQL Editor → New Query → Run
-- ============================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS tbl_users (
    id_user SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    security_question TEXT,
    security_answer TEXT,
    telegram_id TEXT UNIQUE,
    dcompdate TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de categorías
CREATE TABLE IF NOT EXISTS tbl_category (
    id_category SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    id_subcategory INTEGER REFERENCES tbl_category(id_category),
    type_category TEXT NOT NULL DEFAULT 'gasto',
    dcompdate TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS tbl_transactions (
    id_txn SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type_txn TEXT NOT NULL,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    id_category INTEGER REFERENCES tbl_category(id_category),
    dcompdate TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de presupuestos
CREATE TABLE IF NOT EXISTS tbl_budgets (
    id SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    id_category INTEGER NOT NULL REFERENCES tbl_category(id_category),
    amount_limit REAL NOT NULL,
    UNIQUE(id_user, id_category)
);

-- Tabla de gastos fijos
CREATE TABLE IF NOT EXISTS tbl_recurring (
    id SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type_txn TEXT NOT NULL,
    id_category INTEGER REFERENCES tbl_category(id_category),
    day_of_month INTEGER NOT NULL,
    last_processed_month TEXT
);

-- ============================================
-- CATEGORÍAS PRINCIPALES DE GASTOS (IDs 1-10)
-- ============================================
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (1, 'Alimentacion', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (2, 'Transporte', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (3, 'Educacion', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (4, 'Salud', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (5, 'Entretenimiento', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (6, 'Vivienda', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (7, 'Servicios', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (8, 'Ropa', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (9, 'Tecnologia', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (10, 'Otros Gastos', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (47, 'Tarjetas de Credito', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (48, 'Prestamos', NULL, 'gasto') ON CONFLICT (id_category) DO NOTHING;

-- ============================================
-- CATEGORÍAS PRINCIPALES DE INGRESOS
-- ============================================
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (11, 'Salario', NULL, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (12, 'Freelance', NULL, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (13, 'Inversiones', NULL, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (14, 'Ventas', NULL, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (15, 'Otros Ingresos', NULL, 'ingreso') ON CONFLICT (id_category) DO NOTHING;

-- SUBCATEGORÍAS DE GASTOS
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (16, 'Supermercado', 1, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (17, 'Restaurantes', 1, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (18, 'Delivery', 1, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (19, 'Mercado', 1, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (20, 'Combustible', 2, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (21, 'Pasajes', 2, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (22, 'Taxi', 2, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (23, 'Mantenimiento vehicular', 2, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (24, 'Matricula', 3, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (25, 'Mensualidad', 3, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (26, 'Libros y materiales', 3, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (27, 'Cursos online', 3, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (28, 'Consultas medicas', 4, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (29, 'Farmacia', 4, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (30, 'Seguro medico', 4, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (31, 'Cine', 5, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (32, 'Streaming', 5, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (33, 'Viajes', 5, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (34, 'Deportes', 5, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (35, 'Alquiler', 6, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (36, 'Agua', 6, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (37, 'Luz', 6, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (38, 'Internet', 6, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (39, 'Gas', 6, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (40, 'Telefonia', 7, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (41, 'Suscripciones', 7, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (49, 'BCP', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (50, 'Interbank', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (51, 'BBVA', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (52, 'Falabella', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (53, 'Ripley', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (54, 'Scotiabank', 47, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (55, 'Prestamo Personal', 48, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (56, 'Prestamo Hipotecario', 48, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (57, 'Prestamo Vehicular', 48, 'gasto') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (58, 'Prestamo Yape', 48, 'gasto') ON CONFLICT (id_category) DO NOTHING;

-- SUBCATEGORÍAS DE INGRESOS
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (42, 'Sueldo fijo', 11, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (43, 'Horas extra', 11, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (44, 'Bonificaciones', 11, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (45, 'Proyectos', 12, 'ingreso') ON CONFLICT (id_category) DO NOTHING;
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (46, 'Consultoria', 12, 'ingreso') ON CONFLICT (id_category) DO NOTHING;

-- Ajustar la secuencia de autoincremento para evitar colisiones con IDs insertados manualmente
SELECT setval('tbl_category_id_category_seq', (SELECT MAX(id_category) FROM tbl_category));

-- ============================================
-- USUARIO POR DEFECTO (cambia la contraseña después)
-- ============================================
INSERT INTO tbl_users (username, password, security_question, security_answer)
VALUES ('kevin', 'admin', '¿Cual es la clave por defecto?', 'admin')
ON CONFLICT (username) DO NOTHING;
