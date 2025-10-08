# Zoho ↔ D-Tools SI Integration (ZohoSI)

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
