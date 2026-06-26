from database.connection import init_db, get_connection

def setup_database():
    """Inicializa la aplicación: crea la BD si no existe y prepara los datos por defecto."""
    init_db()
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Migración: Añadir columnas de seguridad si no existen (SQLite no soporta IF NOT EXISTS en ALTER, así que usamos PRAGMA)
        cursor.execute("PRAGMA table_info(tbl_users)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'security_question' not in columns:
            cursor.execute("ALTER TABLE tbl_users ADD COLUMN security_question TEXT")
        if 'security_answer' not in columns:
            cursor.execute("ALTER TABLE tbl_users ADD COLUMN security_answer TEXT")
            
        cursor.execute("SELECT id_user, username, security_question FROM tbl_users WHERE username = ?", ('kevin',))
        user = cursor.fetchone()
        if not user:
            # Crear usuario por defecto si no existe
            cursor.execute("INSERT INTO tbl_users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)", ('kevin', 'admin', '¿Cual es la clave por defecto?', 'admin'))
            conn.commit()
        elif user[2] is None:
            # Si el usuario kevin existe pero no tiene pregunta de seguridad, actualizarlo
            cursor.execute("UPDATE tbl_users SET security_question = ?, security_answer = ? WHERE username = ?", ('¿Cual es la clave por defecto?', 'admin', 'kevin'))
            conn.commit()
            
        # Actualización de base de datos para instalaciones existentes (añadir nuevas categorías)
        cursor.execute("SELECT COUNT(*) FROM tbl_category WHERE description = 'Tarjetas de Credito'")
        if cursor.fetchone()[0] == 0:
            # Insertar categorías principales si no existen
            cursor.execute("INSERT INTO tbl_category (id_category, description, type_category) VALUES (?, ?, ?)", (47, 'Tarjetas de Credito', 'gasto'))
            cursor.execute("INSERT INTO tbl_category (id_category, description, type_category) VALUES (?, ?, ?)", (48, 'Prestamos', 'gasto'))
            
            # Insertar subcategorías TC
            bancos = [(49, 'BCP'), (50, 'Interbank'), (51, 'BBVA'), (52, 'Falabella'), (53, 'Ripley'), (54, 'Scotiabank')]
            for id_cat, banco in bancos:
                cursor.execute("INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (?, ?, ?, ?)", (id_cat, banco, 47, 'gasto'))
            
            # Insertar subcategorías Préstamos
            prestamos = [(55, 'Prestamo Personal'), (56, 'Prestamo Hipotecario'), (57, 'Prestamo Vehicular')]
            for id_cat, prest in prestamos:
                cursor.execute("INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (?, ?, ?, ?)", (id_cat, prest, 48, 'gasto'))
                
            conn.commit()
            
        # Añadir Prestamo Yape si no existe (Parche adicional)
        cursor.execute("SELECT COUNT(*) FROM tbl_category WHERE description = 'Prestamo Yape'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO tbl_category (id_category, description, id_subcategory, type_category) VALUES (?, ?, ?, ?)", (58, 'Prestamo Yape', 48, 'gasto'))
            
        # Crear tablas de presupuestos y gastos fijos si no existen (Migración)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
                id_category INTEGER NOT NULL REFERENCES tbl_category(id_category),
                amount_limit REAL NOT NULL,
                UNIQUE(id_user, id_category)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tbl_recurring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL REFERENCES tbl_users(id_user),
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type_txn TEXT NOT NULL,
                id_category INTEGER REFERENCES tbl_category(id_category),
                day_of_month INTEGER NOT NULL,
                last_processed_month TEXT
            )
        """)
        conn.commit()
            
    finally:
        conn.close()
