from database.connection import get_connection
from models.category import Category

# Obtener todas las categorías
def get_all_categories():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_category, description, id_subcategory, type_category
            FROM tbl_category
        """)

        rows = cursor.fetchall()

        categorias = []

        for row in rows:
            categoria = Category(
                id_category=row[0],
                description=row[1],
                id_subcategory=row[2],
                type_category=row[3]
            )
            categorias.append(categoria)

        return categorias
    finally:
        conn.close()


# Crear categoría o subcategoría (devuelve el id asignado)
def create_category(category: Category):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tbl_category (description, id_subcategory, type_category)
            VALUES (?, ?, ?)
        """, (category.description, category.id_subcategory, category.type_category or 'gasto'))

        new_id = cursor.lastrowid
        conn.commit()
        return new_id
    finally:
        conn.close()


# Obtener subcategorías asociadas a una categoría padre
def get_subcategories_by_parent(parent_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_category, description, id_subcategory, type_category
            FROM tbl_category
            WHERE id_subcategory = ?
            ORDER BY description ASC
        """, (parent_id,))

        rows = cursor.fetchall()

        subcategorias = []
        for row in rows:
            subcat = Category(
                id_category=row[0],
                description=row[1],
                id_subcategory=row[2],
                type_category=row[3]
            )
            subcategorias.append(subcat)

        return subcategorias
    finally:
        conn.close()

def get_category_name_by_id(cat_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM tbl_category WHERE id_category = ?", (cat_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()
