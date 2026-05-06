# Cloud Computing Evaluation Starter (FastAPI + Google Cloud)

This repository is a **minimal and intentionally incomplete** starter for a cloud computing evaluation.

The objective is to complete and deploy the API in Google Cloud, integrating multiple managed services.

## What is included

- `main.py` with endpoint stubs and TODO comments
- `requirements.txt` with required dependencies
- `.env.example` with placeholder environment variables
- `app.yaml.example` as a non-working deployment template

## Challenge Requirements

Students must connect FastAPI to:

1. **Cloud SQL PostgreSQL** using `psycopg2`.
2. **Cloud Storage** using the Google Cloud SDK (`google-cloud-storage`).
3. **Firestore** using the Google Cloud SDK (`google-cloud-firestore`).
4. **App Engine Standard** deployment.

## Required API Endpoints

- `GET /health`
- `POST /products`
- `GET /products`
- `POST /products/{product_id}/image`
- `POST /products/{product_id}/comments`
- `GET /audit/events`

## Important Evaluation Notes

- Local execution is only preparation.
- The final evaluation happens in Google Cloud.
- The deployed App Engine app must consume Cloud SQL, Firestore, and Cloud Storage.
- Students are responsible for IAM permissions, service account configuration, environment variables, and deployment troubleshooting.

## Local Preparation (Not the Final Goal)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
uvicorn main:app --reload
```

> Local success does not guarantee cloud evaluation success. Production behavior, IAM, network access, and service wiring must be validated in Google Cloud.
