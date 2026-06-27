"""
telegram_bot/db.py
Funciones de base de datos específicas para el Bot de Telegram.
Compatibles con SQLite (local/testing) y PostgreSQL (producción/Supabase).
"""
from database.connection import get_connection, is_postgres

def _ph(query: str) -> str:
    """Adapta placeholders ? → %s para PostgreSQL."""
    if is_postgres():
        return query.replace('?', '%s')
    return query

def _rows(cursor):
    """Convierte resultados a lista de tuplas planas."""
    rows = cursor.fetchall()
    return [tuple(r) for r in rows] if rows else []

# ─────────────────────────────────────────────
# Autenticación y vinculación de cuentas
# ─────────────────────────────────────────────

def get_user_by_telegram_id(telegram_id: int):
    """Retorna (id_user, username) si el telegram_id está vinculado, o None."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            _ph("SELECT id_user, username FROM tbl_users WHERE telegram_id = ?"),
            (str(telegram_id),)
        )
        row = cur.fetchone()
        return tuple(row) if row else None
    finally:
        conn.close()


def link_telegram_id(username: str, password: str, telegram_id: int):
    """
    Verifica credenciales y vincula el telegram_id con la cuenta.
    Soporta bcrypt (contraseñas hasheadas) y texto plano (legacy, para migración).
    Retorna (True, username) si es exitoso, o (False, mensaje_error).
    """
    import bcrypt

    conn = get_connection()
    if not conn:
        return False, "Error de conexión a la base de datos"
    try:
        cur = conn.cursor()
        cur.execute(
            _ph("SELECT id_user, username, password FROM tbl_users WHERE username = ?"),
            (username.strip(),)
        )
        row = cur.fetchone()
        if not row:
            return False, "Usuario o contraseña incorrectos. Intenta de nuevo."

        user_id, user_name, stored_pw = tuple(row)[0], tuple(row)[1], tuple(row)[2]

        # ── Verificar contraseña: soporta bcrypt Y texto plano (legacy) ──
        pw_bytes = password.strip().encode('utf-8')
        stored_bytes = stored_pw.encode('utf-8') if isinstance(stored_pw, str) else stored_pw

        try:
            # Intenta verificar como hash bcrypt
            pw_ok = bcrypt.checkpw(pw_bytes, stored_bytes)
        except Exception:
            # Fallback: comparación texto plano (para cuentas no migradas)
            pw_ok = (password.strip() == stored_pw)

        if not pw_ok:
            return False, "Usuario o contraseña incorrectos. Intenta de nuevo."

        # Vincular telegram_id
        cur.execute(
            _ph("UPDATE tbl_users SET telegram_id = ? WHERE id_user = ?"),
            (str(telegram_id), user_id)
        )
        conn.commit()
        return True, user_name
    except Exception as e:
        return False, f"Error al vincular cuenta: {str(e)}"
    finally:
        conn.close()



# ─────────────────────────────────────────────
# Transacciones
# ─────────────────────────────────────────────

def insert_transaction_bot(user_id: int, description: str, amount: float,
                            type_txn: str, id_category: int) -> bool:
    """Inserta una transacción desde el bot. Retorna True si fue exitoso."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            _ph("""
                INSERT INTO tbl_transactions (description, amount, type_txn, id_user, id_category)
                VALUES (?, ?, ?, ?, ?)
            """),
            (description, amount, type_txn, user_id, id_category)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"[Bot] Error al insertar transacción: {e}")
        return False
    finally:
        conn.close()


def get_recent_bot(user_id: int, limit: int = 8):
    """
    Retorna las últimas transacciones del usuario.
    Cada fila: (description, amount, type_txn, category_name, dcompdate)
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            _ph("""
                SELECT t.description, t.amount, t.type_txn,
                       COALESCE(c.description, 'Sin categoría') AS cat_name,
                       t.dcompdate
                FROM tbl_transactions t
                LEFT JOIN tbl_category c ON t.id_category = c.id_category
                WHERE t.id_user = ?
                ORDER BY t.dcompdate DESC, t.id_txn DESC
                LIMIT ?
            """),
            (user_id, limit)
        )
        return _rows(cur)
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Resumen financiero
# ─────────────────────────────────────────────

def get_summary_bot(user_id: int) -> dict:
    """Retorna resumen financiero: ingresos, gastos, balance, comparativa mensual."""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = conn.cursor()

        # Totales generales
        cur.execute(
            _ph("""
                SELECT
                    COALESCE(SUM(CASE WHEN type_txn = 'ingreso' THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN type_txn = 'gasto'   THEN amount ELSE 0 END), 0)
                FROM tbl_transactions WHERE id_user = ?
            """),
            (user_id,)
        )
        row = cur.fetchone()
        total_inc, total_exp = float(tuple(row)[0]), float(tuple(row)[1])

        # Gastos del mes actual y mes anterior
        if is_postgres():
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE
                        WHEN type_txn = 'gasto'
                        AND DATE_TRUNC('month', dcompdate) = DATE_TRUNC('month', NOW())
                        THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE
                        WHEN type_txn = 'gasto'
                        AND DATE_TRUNC('month', dcompdate) = DATE_TRUNC('month', NOW() - INTERVAL '1 month')
                        THEN amount ELSE 0 END), 0)
                FROM tbl_transactions WHERE id_user = %s
            """, (user_id,))
        else:
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE
                        WHEN type_txn = 'gasto'
                        AND strftime('%Y-%m', dcompdate) = strftime('%Y-%m', 'now')
                        THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE
                        WHEN type_txn = 'gasto'
                        AND strftime('%Y-%m', dcompdate) = strftime('%Y-%m', date('now','-1 month'))
                        THEN amount ELSE 0 END), 0)
                FROM tbl_transactions WHERE id_user = ?
            """, (user_id,))

        monthly = cur.fetchone()
        this_month = float(tuple(monthly)[0])
        last_month = float(tuple(monthly)[1])

        return {
            'total_income':      total_inc,
            'total_expense':     total_exp,
            'net_balance':       total_inc - total_exp,
            'this_month_expense': this_month,
            'last_month_expense': last_month,
        }
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Categorías
# ─────────────────────────────────────────────

def get_categories_bot(type_txn: str):
    """
    Retorna categorías PRINCIPALES (sin subcategoría) del tipo dado.
    Cada elemento: (id_category, description)
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            _ph("""
                SELECT id_category, description
                FROM tbl_category
                WHERE type_category = ? AND id_subcategory IS NULL
                ORDER BY id_category
            """),
            (type_txn,)
        )
        return _rows(cur)
    finally:
        conn.close()
