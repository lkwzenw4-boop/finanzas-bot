from database.connection import get_connection, adapt_query, is_postgres
from models.transaction import Transaction

# Insertar transacción
def insert_transaction(txn: Transaction):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            INSERT INTO tbl_transactions 
            (description, amount, type_txn, id_user, id_category)
            VALUES (?, ?, ?, ?, ?)
        """), (
            txn.description,
            txn.amount,
            txn.type_txn,
            txn.id_user,
            txn.id_category
        ))
        conn.commit()
    finally:
        conn.close()


# Reporte agrupado por categoría y subcategoría
def get_report_by_category(id_user, type_txn=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if type_txn:
            cursor.execute(adapt_query("""
                SELECT 
                    COALESCE(c_parent.description, c_child.description) AS category,
                    CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END AS subcategory,
                    SUM(t.amount) AS total
                FROM tbl_transactions t
                JOIN tbl_category c_child ON t.id_category = c_child.id_category
                LEFT JOIN tbl_category c_parent ON c_child.id_subcategory = c_parent.id_category
                WHERE t.id_user = ? AND t.type_txn = ?
                GROUP BY COALESCE(c_parent.description, c_child.description), 
                         CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
                ORDER BY total DESC
            """), (id_user, type_txn))
        else:
            cursor.execute(adapt_query("""
                SELECT 
                    COALESCE(c_parent.description, c_child.description) AS category,
                    CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END AS subcategory,
                    SUM(t.amount) AS total
                FROM tbl_transactions t
                JOIN tbl_category c_child ON t.id_category = c_child.id_category
                LEFT JOIN tbl_category c_parent ON c_child.id_subcategory = c_parent.id_category
                WHERE t.id_user = ?
                GROUP BY COALESCE(c_parent.description, c_child.description), 
                         CASE WHEN c_child.id_subcategory IS NOT NULL THEN c_child.description ELSE 'Sin subcategoría' END
                ORDER BY total DESC
            """), (id_user,))

        result = cursor.fetchall()
        return result
    finally:
        conn.close()


def get_financial_summary(id_user):
    conn = get_connection()
    if not conn:
        return {
            "total_income": 0.0,
            "total_expense": 0.0,
            "net_balance": 0.0,
            "last_month_expense": 0.0,
            "this_month_expense": 0.0
        }
    
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            SELECT 
                COALESCE(SUM(CASE WHEN type_txn = 'ingreso' THEN amount ELSE 0 END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type_txn = 'gasto' THEN amount ELSE 0 END), 0) AS total_expense
            FROM tbl_transactions
            WHERE id_user = ?;
        """), (id_user,))
        result = cursor.fetchone()
        
        if is_postgres():
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN TO_CHAR(dcompdate,'YYYY-MM') = TO_CHAR(NOW(),'YYYY-MM') THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN TO_CHAR(dcompdate,'YYYY-MM') = TO_CHAR(NOW() - INTERVAL '1 month','YYYY-MM') THEN amount ELSE 0 END), 0)
                FROM tbl_transactions
                WHERE id_user = %s AND type_txn = 'gasto';
            """, (id_user,))
        else:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN strftime('%Y-%m', dcompdate) = strftime('%Y-%m', 'now') THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN strftime('%Y-%m', dcompdate) = strftime('%Y-%m', 'now', '-1 month') THEN amount ELSE 0 END), 0)
                FROM tbl_transactions
                WHERE id_user = ? AND type_txn = 'gasto';
            """, (id_user,))
        monthly_result = cursor.fetchone()

        total_income = float(result[0]) if result else 0.0
        total_expense = float(result[1]) if result else 0.0
        net_balance = total_income - total_expense
        
        this_month_expense = float(monthly_result[0]) if monthly_result else 0.0
        last_month_expense = float(monthly_result[1]) if monthly_result else 0.0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "this_month_expense": this_month_expense,
            "last_month_expense": last_month_expense
        }
    finally:
        cursor.close()
        conn.close()


def get_recent_transactions(id_user, limit=10, month=None, year=None):
    """Obtiene las últimas transacciones del usuario con nombre de categoría."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        ph = '%s' if is_postgres() else '?'

        base_query = """
            SELECT 
                t.id_txn,
                t.description,
                t.amount,
                t.type_txn,
                COALESCE(c.description, 'Sin categoría') AS category_name,
                t.dcompdate
            FROM tbl_transactions t
            LEFT JOIN tbl_category c ON t.id_category = c.id_category
            WHERE t.id_user = {ph}
        """.format(ph=ph)
        params = [id_user]

        if month and month != "Todos":
            if is_postgres():
                base_query += " AND TO_CHAR(t.dcompdate, 'MM') = %s"
            else:
                base_query += " AND strftime('%m', t.dcompdate) = ?"
            params.append(month.zfill(2))

        if year and year != "Todos":
            if is_postgres():
                base_query += " AND TO_CHAR(t.dcompdate, 'YYYY') = %s"
            else:
                base_query += " AND strftime('%Y', t.dcompdate) = ?"
            params.append(str(year))

        base_query += " ORDER BY t.dcompdate DESC, t.id_txn DESC LIMIT {ph}".format(ph=ph)
        params.append(limit)

        cursor.execute(base_query, tuple(params))
        result = cursor.fetchall()
        return [tuple(row) for row in result]
    finally:
        cursor.close()
        conn.close()

def update_transaction(id_txn, amount, description, id_category):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            UPDATE tbl_transactions
            SET amount = ?, description = ?, id_category = ?
            WHERE id_txn = ?
        """), (amount, description, id_category, id_txn))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_transaction(id_txn):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("DELETE FROM tbl_transactions WHERE id_txn = ?"), (id_txn,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_category_from_history(id_user, desc):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            SELECT id_category FROM tbl_transactions 
            WHERE id_user = ? AND LOWER(TRIM(description)) = LOWER(TRIM(?)) 
            ORDER BY id_txn DESC LIMIT 1
        """), (id_user, desc))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()

# ===================== PRESUPUESTOS =====================
def set_budget(id_user, id_category, amount_limit):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            INSERT INTO tbl_budgets (id_user, id_category, amount_limit)
            VALUES (?, ?, ?)
            ON CONFLICT(id_user, id_category) DO UPDATE SET amount_limit=excluded.amount_limit
        """), (id_user, id_category, amount_limit))
        conn.commit()
    finally:
        conn.close()

def get_budgets(id_user):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        if is_postgres():
            cursor.execute("""
                SELECT 
                    b.id_category, c.description, b.amount_limit,
                    COALESCE((SELECT SUM(amount) FROM tbl_transactions 
                              WHERE id_user=b.id_user AND id_category=b.id_category AND type_txn='gasto' 
                              AND TO_CHAR(dcompdate, 'YYYY-MM') = TO_CHAR(NOW(), 'YYYY-MM')), 0) as spent
                FROM tbl_budgets b
                JOIN tbl_category c ON b.id_category = c.id_category
                WHERE b.id_user = %s
            """, (id_user,))
        else:
            cursor.execute("""
                SELECT 
                    b.id_category, c.description, b.amount_limit,
                    COALESCE((SELECT SUM(amount) FROM tbl_transactions 
                              WHERE id_user=b.id_user AND id_category=b.id_category AND type_txn='gasto' 
                              AND strftime('%Y-%m', dcompdate) = strftime('%Y-%m', 'now')), 0) as spent
                FROM tbl_budgets b
                JOIN tbl_category c ON b.id_category = c.id_category
                WHERE b.id_user = ?
            """, (id_user,))
        return [tuple(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# ===================== GASTOS FIJOS (RECURRING) =====================
def add_recurring(id_user, description, amount, type_txn, id_category, day_of_month):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            INSERT INTO tbl_recurring (id_user, description, amount, type_txn, id_category, day_of_month)
            VALUES (?, ?, ?, ?, ?, ?)
        """), (id_user, description, amount, type_txn, id_category, day_of_month))
        conn.commit()
    finally:
        conn.close()

def get_recurring(id_user):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("""
            SELECT r.id, r.description, r.amount, r.type_txn, c.description as cat_name, r.day_of_month, r.last_processed_month
            FROM tbl_recurring r
            LEFT JOIN tbl_category c ON r.id_category = c.id_category
            WHERE r.id_user = ?
        """), (id_user,))
        return [tuple(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def skip_recurring_month(rec_id, month_str):
    import datetime
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        
        # Obtener detalles del gasto recurrente para buscar su transacción automática
        cursor.execute(adapt_query("SELECT id_user, description, id_category FROM tbl_recurring WHERE id = ?"), (rec_id,))
        rec = cursor.fetchone()
        
        if rec:
            id_user, desc, id_category = rec
            auto_desc = f"{desc} (Automático)"
            current_month = datetime.datetime.now().strftime('%Y-%m')
            
            # Buscar y eliminar la transacción generada este mes
            if is_postgres():
                cursor.execute("""
                    DELETE FROM tbl_transactions 
                    WHERE id_user = %s AND id_category = %s AND description = %s
                    AND TO_CHAR(dcompdate, 'YYYY-MM') = %s
                """, (id_user, id_category, auto_desc, current_month))
            else:
                cursor.execute("""
                    DELETE FROM tbl_transactions 
                    WHERE id_user = ? AND id_category = ? AND description = ?
                    AND strftime('%Y-%m', dcompdate) = ?
                """, (id_user, id_category, auto_desc, current_month))

        # Actualizar el estado del gasto recurrente
        cursor.execute(adapt_query(
            "UPDATE tbl_recurring SET last_processed_month = ? WHERE id = ?"
        ), (month_str, rec_id))
        conn.commit()
    finally:
        conn.close()

def delete_recurring(rec_id):
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute(adapt_query("DELETE FROM tbl_recurring WHERE id = ?"), (rec_id,))
        conn.commit()
    finally:
        conn.close()

def process_recurring_transactions(id_user):
    import datetime
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now()
        current_month = now.strftime('%Y-%m')
        current_day = now.day

        cursor.execute(adapt_query(
            "SELECT id, description, amount, type_txn, id_category, day_of_month "
            "FROM tbl_recurring WHERE id_user = ? "
            "AND (last_processed_month IS NULL OR last_processed_month != ?)"
        ), (id_user, current_month))
        recs = cursor.fetchall()

        for r in recs:
            if current_day >= r[5]:  # Si ya pasó o es el día de cobro
                cursor.execute(adapt_query("""
                    INSERT INTO tbl_transactions (description, amount, type_txn, id_user, id_category)
                    VALUES (?, ?, ?, ?, ?)
                """), (f"{r[1]} (Automático)", r[2], r[3], id_user, r[4]))
                cursor.execute(adapt_query(
                    "UPDATE tbl_recurring SET last_processed_month = ? WHERE id = ?"
                ), (current_month, r[0]))

        conn.commit()
    finally:
        conn.close()