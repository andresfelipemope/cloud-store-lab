import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID")
AUDIT_COLLECTION = os.getenv("FIRESTORE_COLLECTION_AUDIT_EVENTS")
COMMENTS_COLLECTION = os.getenv("FIRESTORE_COLLECTION_COMMENTS")


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


