import os
import psycopg2
import firestore_service

from dotenv import load_dotenv

load_dotenv()

def get_connection():
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    return conn

def create_product(payload):
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = """ 
        INSERT INTO product(name, description, price)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, price, img_url, created_at;
    """
    
    cursor.execute(sql, (payload.name, payload.description, payload.price))
    
    product = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    firestore_service.write_audit_event(
        event_type="product_created",
        data={
            "message": "Product created successfully",
            "product_id": product[0],
            "name": product[1],
            "description": product[2],
            "price": float(product[3]),
        }
    )
    
    return {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "price": float(product[3]),
        "img_url": product[4],
        "created_at": str(product[5])
    }
    
def get_products(
    page: int = 1,
    page_size: int = 5,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    where_clauses = []
    params: list[object] = []

    if name:
        where_clauses.append("name ILIKE %s")
        params.append(f"%{name}%")
    if min_price is not None:
        where_clauses.append("price >= %s")
        params.append(min_price)
    if max_price is not None:
        where_clauses.append("price <= %s")
        params.append(max_price)

    where_sql = ""
    if where_clauses:
        where_sql = " WHERE " + " AND ".join(where_clauses)

    count_sql = f"SELECT COUNT(*) FROM product{where_sql};"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]

    offset = (page - 1) * page_size
    sql = f"""
        SELECT id, name, description, price, img_url, created_at
        FROM product{where_sql}
        ORDER BY created_at DESC, id DESC
        LIMIT %s OFFSET %s;
    """

    query_params = params + [page_size, offset]
    cursor.execute(sql, query_params)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    result = []
    for product in products:
        result.append(
            {
                "id": product[0],
                "name": product[1],
                "description": product[2],
                "price": float(product[3]),
                "img_url": product[4],
                "created_at": str(product[5])
            }
        )

    firestore_service.write_audit_event(
        event_type="products_listed",
        data={
            "message": "Products listed successfully",
            "results": result
        }
    )

    return {
        "products": result,
        "total": total,
    }


def product_exists(product_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM product WHERE id = %s LIMIT 1", (product_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()