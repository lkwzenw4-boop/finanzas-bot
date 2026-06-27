import sqlite3
import os

# ─────────────────────────────────────────────
# Modo dual: SQLite (local) o PostgreSQL (nube)
# Si existe la variable DATABASE_URL → PostgreSQL
# Si no existe → SQLite local
# ─────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')

# Mantener la conexión abierta
_pg_conn = None

class PooledConnection:
    """Proxy para evitar que los servicios cierren la conexión compartida."""
    def __init__(self, conn):
        self._conn = conn
    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)
    def commit(self):
        self._conn.commit()
    def rollback(self):
        self._conn.rollback()
    def close(self):
        pass # Ignorar el cierre

def is_postgres():
    """Retorna True si se está usando PostgreSQL."""
    return bool(DATABASE_URL)

def adapt_query(query: str) -> str:
    """Convierte placeholders ? de SQLite a %s de PostgreSQL."""
    if is_postgres():
        return query.replace('?', '%s')
    return query

def get_db_path():
    """Retorna la ruta de la base de datos SQLite (junto al exe o main.py)."""
    from utils.paths import get_user_data_path
    return os.path.join(get_user_data_path(), 'finanzas.db')

def get_connection():
    """Retorna una conexión a la BD activa (SQLite o PostgreSQL)."""
    if DATABASE_URL:
        # ── Modo PostgreSQL (Nube / Telegram Bot) ──
        try:
            global _pg_conn
            import psycopg2
            if _pg_conn is None or _pg_conn.closed:
                _pg_conn = psycopg2.connect(DATABASE_URL)
            return PooledConnection(_pg_conn)
        except Exception as e:
            print("[Error] Fallo la conexion a PostgreSQL:", e)
            return None
    else:
        # ── Modo SQLite (App de Escritorio) ──
        try:
            from utils.paths import get_user_data_path
            db_path = os.path.join(get_user_data_path(), 'finanzas.db')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print("[Error] Fallo la conexion a SQLite:", e)
            return None

def init_db():
    """Inicializa la base de datos SQLite si no existe (primera ejecución)."""
    if DATABASE_URL:
        return  # En modo PostgreSQL, el schema se aplica manualmente en Supabase

    from utils.paths import get_base_path, get_user_data_path
    db_path = os.path.join(get_user_data_path(), 'finanzas.db')
    if os.path.exists(db_path):
        _migrate_db()  # Ejecutar migraciones si ya existe
        return

    schema_path = os.path.join(get_base_path(), 'database', 'schema.sql')
    try:
        conn = sqlite3.connect(db_path)
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.close()
        print("[OK] Base de datos creada exitosamente.")
        _migrate_db()
    except Exception as e:
        print("[Error] Error al inicializar la BD:", e)

def _migrate_db():
    """Ejecuta migraciones incrementales (añadir columnas nuevas si no existen)."""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        # Migración 1: Añadir telegram_id a tbl_users (para integración Telegram)
        # Nota: SQLite no permite ADD COLUMN UNIQUE, lo manejamos sin esa restricción
        try:
            cursor.execute("ALTER TABLE tbl_users ADD COLUMN telegram_id TEXT")
            conn.commit()
            print("[OK] Migración: columna telegram_id añadida.")
        except Exception:
            pass  # La columna ya existe, ignorar
        conn.close()
    except Exception as e:
        print(f"[Warn] Error en migración: {e}")