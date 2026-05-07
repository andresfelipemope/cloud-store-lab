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
        "SELECT id FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if product is None:
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

    return blob.public_url