from database.connection import get_connection
from models.user import User

# Crear usuario
def create_user(user: User):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tbl_users (username, password, security_question, security_answer)
            VALUES (?, ?, ?, ?)
        """, (user.username, user.password, user.security_question, user.security_answer))

        user_id = cursor.lastrowid
        conn.commit()

        return user_id
    finally:
        conn.close()


# Login básico
def login(username, password):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_user, username
            FROM tbl_users
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()

        return user  # None si no existe
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_user, username
            FROM tbl_users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        return user  # None si no existe
    finally:
        conn.close()

def get_security_question(username):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT security_question FROM tbl_users WHERE username = ?", (username,))
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
        # Verificar respuesta (case-insensitive for better UX in some cases, but exact match is safer)
        cursor.execute("SELECT id_user FROM tbl_users WHERE username = ? AND security_answer = ?", (username, answer))
        if cursor.fetchone():
            cursor.execute("UPDATE tbl_users SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()
            return True
        return False
    finally:
        conn.close()