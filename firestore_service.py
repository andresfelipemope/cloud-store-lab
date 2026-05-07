import os
from google.cloud import firestore
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
DATABASE_ID = os.getenv("FIRESTORE_DATABASE_ID")

AUDIT_COLLECTION = os.getenv(
    "FIRESTORE_COLLECTION_AUDIT_EVENTS",
    "audit_events"
)

COMMENTS_COLLECTION = os.getenv(
    "FIRESTORE_COLLECTION_COMMENTS",
    "product_comments"
)


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


