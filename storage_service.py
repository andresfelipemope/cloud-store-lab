import os

from fastapi import UploadFile, HTTPException
from google.cloud import storage
from dotenv import load_dotenv
import database

load_dotenv()

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_image_to_gcs(product_id: int, file: UploadFile):

    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM product WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()
    
    
    if product is None:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    client = storage.Client()

    bucket = client.bucket(BUCKET_NAME)

    extension = file.filename.split(".")[-1]

    blob_path = f"products/{product_id}/image.{extension}"

    blob = bucket.blob(blob_path)

    blob.upload_from_file(
        file.file,
        content_type=file.content_type
    )
    
    sql = """
        UPDATE product
        SET img_url = %s
        WHERE id = %s;
    """
    
    cursor.execute(sql, (blob.public_url, product_id))
    
    conn.commit()
    
    cursor.close()
    conn.close()

    return blob.public_url