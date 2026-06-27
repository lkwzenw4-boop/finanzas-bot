from database.connection import get_connection, adapt_query
from models.user import User

# Crear usuario
def create_user(user: User):
    conn = get_connection()
    try:
        import bcrypt
        
        # Encriptar contraseña
        salt_pw = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), salt_pw).decode('utf-8')
        
        # Encriptar respuesta de seguridad
        salt_ans = bcrypt.gensalt()
        hashed_ans = bcrypt.hashpw(user.security_answer.lower().encode('utf-8'), salt_ans).decode('utf-8')
        
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            INSERT INTO tbl_users (username, password, security_question, security_answer)
            VALUES (?, ?, ?, ?)
        """), (user.username, hashed_pw, user.security_question, hashed_ans))

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
        # 1. Obtener la respuesta de seguridad almacenada
        cursor.execute(adapt_query(
            "SELECT security_answer FROM tbl_users WHERE username = ?"
        ), (username,))
        row = cursor.fetchone()
        
        if not row:
            return False
            
        stored_ans = row[0] if hasattr(row, '__getitem__') else tuple(row)[0]
        input_ans = answer.lower()
        
        # 2. Verificar la respuesta (soporta bcrypt y texto plano legacy)
        ans_ok = False
        try:
            import bcrypt
            ans_bytes = input_ans.encode('utf-8')
            stored_bytes = stored_ans.encode('utf-8') if isinstance(stored_ans, str) else stored_ans
            ans_ok = bcrypt.checkpw(ans_bytes, stored_bytes)
        except Exception:
            # Fallback para texto plano
            ans_ok = (input_ans == str(stored_ans).lower())
            
        if not ans_ok:
            return False
            
        # 3. Hashear la nueva contraseña
        import bcrypt
        hashed_new_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # 4. Actualizar contraseña
        cursor.execute(adapt_query(
            "UPDATE tbl_users SET password = ? WHERE username = ?"
        ), (hashed_new_pw, username))
        conn.commit()
        return True
    finally:
        conn.close()