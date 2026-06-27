from database.connection import get_connection, adapt_query
from models.user import User

# Crear usuario
def create_user(user: User):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            INSERT INTO tbl_users (username, password, security_question, security_answer)
            VALUES (?, ?, ?, ?)
        """), (user.username, user.password, user.security_question, user.security_answer))

        # lastrowid funciona en SQLite; en PostgreSQL usamos RETURNING
        try:
            user_id = cursor.lastrowid
        except Exception:
            user_id = None
        conn.commit()
        return user_id
    finally:
        conn.close()


# Login básico — compatible con bcrypt y texto plano
def login(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            SELECT id_user, username, password
            FROM tbl_users
            WHERE username = ?
        """), (username,))
        row = cursor.fetchone()
        if not row:
            return None

        stored_pw = row[2] if hasattr(row, '__getitem__') else tuple(row)[2]
        user_id   = row[0] if hasattr(row, '__getitem__') else tuple(row)[0]
        user_name = row[1] if hasattr(row, '__getitem__') else tuple(row)[1]

        # Verificar contraseña: soporta bcrypt y texto plano (legacy)
        try:
            import bcrypt
            pw_bytes = password.encode('utf-8')
            stored_bytes = stored_pw.encode('utf-8') if isinstance(stored_pw, str) else stored_pw
            pw_ok = bcrypt.checkpw(pw_bytes, stored_bytes)
        except Exception:
            pw_ok = (password == stored_pw)

        if pw_ok:
            # Devolver tupla (id_user, username) igual que antes
            return (user_id, user_name)
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            SELECT id_user, username
            FROM tbl_users
            WHERE username = ?
        """), (username,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_security_question(username):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query(
            "SELECT security_question FROM tbl_users WHERE username = ?"
        ), (username,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def reset_password(username, answer, new_password):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query(
            "SELECT id_user FROM tbl_users WHERE username = ? AND security_answer = ?"
        ), (username, answer))
        if cursor.fetchone():
            cursor.execute(adapt_query(
                "UPDATE tbl_users SET password = ? WHERE username = ?"
            ), (new_password, username))
            conn.commit()
            return True
        return False
    finally:
        conn.close()