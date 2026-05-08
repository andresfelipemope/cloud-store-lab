import os
import psycopg2

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
    
    return {
        "id": product[0],
        "name": product[1],
        "description": product[2],
        "price": float(product[3]),
        "img_url": product[4],
        "created_at": str(product[5])
    }
    
def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = """ 
        SELECT id, name, description, price, img_url, created_at
        FROM product;
    """
    
    cursor.execute(sql)
    
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
    
    return result


def product_exists(product_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM product WHERE id = %s LIMIT 1", (product_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()