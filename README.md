# Zoho ↔ D-Tools SI Integration (ZohoSI)

Comprehensive Django + Django REST Framework project that integrates Zoho CRM with D-Tools SI (System Integrator). This repository provides API endpoints, database models, and wrapper clients to coordinate creation and synchronization of deals/projects between Zoho CRM and D-Tools SI.

## Purpose

This service acts as an integration layer that:

- Accepts inbound requests (via DRF endpoints) to push CRM Deal data into D-Tools SI as projects.
- Receives or polls updates from D-Tools SI and applies those updates back to Zoho CRM (field updates and notes).
- Persists requests/operations in a simple SQLite-backed database for audit, retry, and administrative inspection.

The design aims for clarity and ease-of-maintenance rather than heavy abstraction. Wrapper classes isolate external API details so the core logic in views stays concise.

## Repository layout

- `manage.py`
- `db.sqlite3`
- `requirements.txt`
- `start.sh` 
- `zohosi/` 
- `api/` 
  - `views.py` 
  - `models.py`
  - `serializers.py`
  - `SIWrapper.py`
  - `CRMWrapper.py`
  - `SQLDriver.py`
  - `tests.py`
  - `urls.py`
- `core/`
- `templates/`

## API endpoints (concise reference)

- `POST /api/si/` — Create a `SendToSI` record and push the deal to D-Tools SI (handled by `api.views.PushSendToSI`). The request body is expected to match the `StringBoolSerializer` schema.
- `GET/PUT/DELETE /api/si/<pk>/` — Retrieve, update, or delete a `SendToSI` record (`api.views.PullSendToSI`).
- `POST /api/crm/` — Create a `SendToCRM` record and, for updates, fetch projects from SI then update Zoho CRM (`api.views.PushSendToCRM`). Expects data matching `CRMSerializer`.

## License

Proprietary — for internal use only.

## Contact

Author: Aidan Lelliott | 
Organization: Atlanta Soundworks
