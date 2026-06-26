-- ============================================
-- SCHEMA: Finanzas Personales (SQLite)
-- ============================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS tbl_users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    security_question TEXT,
    security_answer TEXT,
    dcompdate TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías (las subcategorías referencian al padre vía id_subcategory)
CREATE TABLE IF NOT EXISTS tbl_category (
    id_category INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    id_subcategory INTEGER NULL REFERENCES tbl_category(id_category),
    type_category TEXT NOT NULL DEFAULT 'gasto',
    dcompdate TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS tbl_transactions (
    id_txn INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type_txn TEXT NOT NULL,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    id_category INTEGER REFERENCES tbl_category(id_category),
    dcompdate TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DATOS INICIALES: Categorías principales (gastos)
-- IDs 1-10 para categorías padre de gastos
-- ============================================
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (1, 'Alimentacion', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (2, 'Transporte', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (3, 'Educacion', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (4, 'Salud', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (5, 'Entretenimiento', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (6, 'Vivienda', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (7, 'Servicios', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (8, 'Ropa', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (9, 'Tecnologia', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (10, 'Otros Gastos', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (47, 'Tarjetas de Credito', NULL, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (48, 'Prestamos', NULL, 'gasto');

-- ============================================
-- DATOS INICIALES: Categorías principales (ingresos)
-- IDs 11-15 para categorías padre de ingresos
-- ============================================
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (11, 'Salario', NULL, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (12, 'Freelance', NULL, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (13, 'Inversiones', NULL, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (14, 'Ventas', NULL, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (15, 'Otros Ingresos', NULL, 'ingreso');

-- ============================================
-- SUBCATEGORÍAS DE GASTOS
-- ============================================

-- Subcategorías de Alimentacion (padre id=1)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (16, 'Supermercado', 1, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (17, 'Restaurantes', 1, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (18, 'Delivery', 1, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (19, 'Mercado', 1, 'gasto');

-- Subcategorías de Transporte (padre id=2)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (20, 'Combustible', 2, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (21, 'Pasajes', 2, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (22, 'Taxi', 2, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (23, 'Mantenimiento vehicular', 2, 'gasto');

-- Subcategorías de Educacion (padre id=3)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (24, 'Matricula', 3, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (25, 'Mensualidad', 3, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (26, 'Libros y materiales', 3, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (27, 'Cursos online', 3, 'gasto');

-- Subcategorías de Salud (padre id=4)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (28, 'Consultas medicas', 4, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (29, 'Farmacia', 4, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (30, 'Seguro medico', 4, 'gasto');

-- Subcategorías de Entretenimiento (padre id=5)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (31, 'Cine', 5, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (32, 'Streaming', 5, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (33, 'Viajes', 5, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (34, 'Deportes', 5, 'gasto');

-- Subcategorías de Vivienda (padre id=6)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (35, 'Alquiler', 6, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (36, 'Agua', 6, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (37, 'Luz', 6, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (38, 'Internet', 6, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (39, 'Gas', 6, 'gasto');

-- Subcategorías de Servicios (padre id=7)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (40, 'Telefonia', 7, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (41, 'Suscripciones', 7, 'gasto');

-- Subcategorías de Tarjetas de Credito (padre id=47)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (49, 'BCP', 47, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (50, 'Interbank', 47, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (51, 'BBVA', 47, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (52, 'Falabella', 47, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (53, 'Ripley', 47, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (54, 'Scotiabank', 47, 'gasto');

-- Subcategorías de Prestamos (padre id=48)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (55, 'Prestamo Personal', 48, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (56, 'Prestamo Hipotecario', 48, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (57, 'Prestamo Vehicular', 48, 'gasto');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (58, 'Prestamo Yape', 48, 'gasto');

-- ============================================
-- SUBCATEGORÍAS DE INGRESOS
-- ============================================

-- Subcategorías de Salario (padre id=11)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (42, 'Sueldo fijo', 11, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (43, 'Horas extra', 11, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (44, 'Bonificaciones', 11, 'ingreso');

-- Subcategorías de Freelance (padre id=12)
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (45, 'Proyectos', 12, 'ingreso');
INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (46, 'Consultoria', 12, 'ingreso');

-- ============================================
-- USUARIO POR DEFECTO
-- ============================================
INSERT INTO tbl_users (username, password, security_question, security_answer) VALUES ('kevin', 'admin', '¿Cual es la clave por defecto?', 'admin');

-- ============================================
-- PRESUPUESTOS Y GASTOS FIJOS
-- ============================================
CREATE TABLE IF NOT EXISTS tbl_budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    id_category INTEGER NOT NULL REFERENCES tbl_category(id_category),
    amount_limit REAL NOT NULL,
    UNIQUE(id_user, id_category)
);

CREATE TABLE IF NOT EXISTS tbl_recurring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type_txn TEXT NOT NULL,
    id_category INTEGER REFERENCES tbl_category(id_category),
    day_of_month INTEGER NOT NULL,
    last_processed_month TEXT
);
