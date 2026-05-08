"""
Minimal FastAPI teaching app for cloud evaluation.

This file is intentionally incomplete. Students must implement:
- Cloud SQL (PostgreSQL) integration
- Cloud Storage integration
- Firestore integration
"""
import database

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Query,
)
from pydantic import BaseModel
from storage_service import upload_image_to_gcs
import firestore_service

app = FastAPI(title="Cloud Computing Evaluation API (Starter)")


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class CommentCreate(BaseModel):
    author: str
    text: str

@app.get("/health")
def health():
    errors: dict[str, str] = {}
    try:
        firestore_service.firestore_audit_events_check()
    except Exception as e:
        errors["audit_events"] = str(e)
    try:
        firestore_service.firestore_product_comments_check()
    except Exception as e:
        errors["product_comments"] = str(e)
    if errors:
        raise HTTPException(status_code=500, detail=errors)
    return {
        "status": "ok",
        "firestore": {"audit_events": "ok", "product_comments": "ok"},
        "app": "Cloud Computing Evaluation API",
    }


@app.post("/products")
def create_product(payload: ProductCreate):
    # TODO: Validate and store product data in Cloud SQL (PostgreSQL).
    # Do not keep products in memory for the final solution.
    # Students should use psycopg2 and proper SQL schema design.
    return database.create_product(payload)


@app.get("/products")
def list_products(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    page_size: int = Query(5, ge=1, le=100, description="Number of products per page"),
    name: str | None = Query(None, description="Filter products by partial name match"),
    min_price: float | None = Query(None, ge=0, description="Filter products with price >= this value"),
    max_price: float | None = Query(None, ge=0, description="Filter products with price <= this value"),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price",
        )

    result = database.get_products(
        page=page,
        page_size=page_size,
        name=name,
        min_price=min_price,
        max_price=max_price,
    )

    return {
        "page": page,
        "page_size": page_size,
        "filters": {
            "name": name,
            "min_price": min_price,
            "max_price": max_price,
        },
        "count": len(result["products"]),
        "total": result["total"],
        "products": result["products"],
    }


@app.post("/products/{product_id}/image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...)
):
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    try:

        img_url = upload_image_to_gcs(product_id, file)

        return {
            "message": "Image uploaded successfully",
            "product_id": product_id,
            "img_url": img_url
        }
    
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/products/{product_id}/comments")
def add_product_comment(product_id: int, payload: CommentCreate):
    if not database.product_exists(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    if not payload.author.strip():
        raise HTTPException(status_code=400, detail="Author is required")
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Comment text is required")

    try:
        comment = firestore_service.add_product_comment(
            product_id=product_id,
            author=payload.author,
            text=payload.text,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Firestore error: {e}",
        ) from e

    return {
        "message": "Comment created successfully",
        "comment": comment,
    }


@app.get("/audit/events")
def get_audit_events(
    limit: int = 50,
    event_type: str | None = None,
    product_id: int | None = None,
):
    max_lim = firestore_service.MAX_AUDIT_QUERY_LIMIT
    if limit < 1 or limit > max_lim:
        raise HTTPException(
            status_code=400,
            detail=f"limit must be between 1 and {max_lim} (inclusive), got {limit}",
        )

    try:
        events = firestore_service.list_audit_events(
            limit=limit,
            event_type=event_type,
            product_id=product_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Firestore error: {e}",
        ) from e
    return {
        "applied": {
            "limit": limit,
            "event_type": event_type,
            "product_id": product_id,
        },
        "count": len(events),
        "events": events,
    }
