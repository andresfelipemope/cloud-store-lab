import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID")
AUDIT_COLLECTION = os.getenv("FIRESTORE_COLLECTION_AUDIT_EVENTS")
COMMENTS_COLLECTION = os.getenv("FIRESTORE_COLLECTION_COMMENTS")

_MAX_AUDIT_LIMIT = 100


def get_firestore_client():
    if DATABASE_ID:
        return firestore.Client(project=PROJECT_ID, database=DATABASE_ID)
    return firestore.Client(project=PROJECT_ID)


def write_audit_event(event_type: str, data: dict | None = None):
    payload = dict(data) if data else {}
    db = get_firestore_client()

    event = {
        "event_type": event_type,
        "data": payload,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    doc_ref = db.collection(AUDIT_COLLECTION).document()
    doc_ref.set(event)

    return {
        "id": doc_ref.id,
        "event_type": event_type,
        "data": payload,
    }

def add_product_comment(product_id: int, author: str, text: str):
    db = get_firestore_client()

    comment = {
        "product_id": product_id,
        "author": author,
        "text": text,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    doc_ref = db.collection(COMMENTS_COLLECTION).document()
    doc_ref.set(comment)

    write_audit_event(
        event_type="comment_created",
        data={
            "product_id": product_id,
            "message": "Product comment created successfully",
            "comment_id": doc_ref.id,
            "author": author,
        },
    )

    return {
        "id": doc_ref.id,
        "product_id": product_id,
        "author": author,
        "text": text,
    }

def _normalize_audit_limit(limit: int) -> int:
    if limit < 1:
        return 1
    return min(limit, _MAX_AUDIT_LIMIT)


def list_audit_events(
    limit: int = 50,
    event_type: str | None = None,
    product_id: int | None = None,
):
    db = get_firestore_client()
    capped = _normalize_audit_limit(limit)

    query = db.collection(AUDIT_COLLECTION)
    if event_type is not None and event_type.strip():
        query = query.where("event_type", "==", event_type.strip())
    if product_id is not None:
        query = query.where("data.product_id", "==", product_id)

    docs = query.order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).limit(capped).stream()

    events = []
    for doc in docs:
        event = doc.to_dict()
        event["id"] = doc.id

        created_at = event.get("created_at")
        if created_at is not None:
            event["created_at"] = created_at.isoformat()

        events.append(event)

    return events


