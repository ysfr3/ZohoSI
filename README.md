# Zoho ↔ D-Tools SI Integration (ZohoSI)

Comprehensive Django + Django REST Framework project that integrates Zoho CRM with D-Tools SI (System Integrator). This repository provides API endpoints, database models, and wrapper clients to coordinate creation and synchronization of deals/projects between Zoho CRM and D-Tools SI.

## Purpose

This service acts as an integration layer that:

- Accepts inbound requests (via DRF endpoints) to push CRM Deal data into D-Tools SI as projects.
- Receives or polls updates from D-Tools SI and applies those updates back to Zoho CRM (field updates and notes).
- Persists requests/operations in a simple SQLite-backed database for audit, retry, and administrative inspection.

The design aims for clarity and ease-of-maintenance rather than heavy abstraction. Wrapper classes isolate external API details so the core logic in views stays concise.

## Repository layout

- `manage.py` — Django CLI entrypoint
- `db.sqlite3` — default SQLite database (development)
- `requirements.txt` — Python dependency pins
- `start.sh` — optional startup script
- `zohosi/` — Django project package (settings, urls, wsgi/asgi)
- `api/` — application package containing the integration logic
  - `views.py` — DRF views that implement the integration workflows
  - `models.py` — Django models: `SendToSI`, `SendToCRM` (persist requests)
  - `serializers.py` — DRF serializers used by the views
  - `SIWrapper.py` — client wrapper for D-Tools SI API
  - `CRMWrapper.py` — client wrapper for Zoho CRM API
  - `SQLDriver.py` — optional helper for direct SQL Server interactions
  - `tests.py` — unit/integration tests for the app
  - `urls.py` — API routing for the app
- `core/` — likely small app for additional views/models
- `templates/` — contains `index.html` landing page

## High-level architecture and flow

1. A client posts a payload to the API endpoint for sending a Deal to SI (`PushSendToSI`). The payload is validated and saved to the `SendToSI` model.
2. On create, the view uses `SIWrapper` to create a project on D-Tools SI. The response containing the SI Project ID is then applied back to the Zoho CRM Deal via `CRMWrapper.push_new_deal_data`.
3. Separately, the `PushSendToCRM` endpoint accepts requests describing a CRM update operation. For `Type == "Update"`, it iterates the provided SI project IDs, calls `SIWrapper.get_project` for each, and updates the corresponding Zoho Deal (fields and notes). Change orders (COs) are appended as notes.

The wrappers abstract authentication, token refresh, and request shaping for each external API.

## API endpoints (concise reference)

- `POST /api/si/` — Create a `SendToSI` record and push the deal to D-Tools SI (handled by `api.views.PushSendToSI`). The request body is expected to match the `StringBoolSerializer` schema.
- `GET/PUT/DELETE /api/si/<pk>/` — Retrieve, update, or delete a `SendToSI` record (`api.views.PullSendToSI`).
- `POST /api/crm/` — Create a `SendToCRM` record and, for updates, fetch projects from SI then update Zoho CRM (`api.views.PushSendToCRM`). Expects data matching `CRMSerializer`.

Refer to `api/serializers.py` for the exact expected JSON shapes.

## Models (conceptual)

- SendToSI
  - Stores inbound requests intended for D-Tools SI. Useful fields include Deal identifiers, Account name, Deal name, Progress, and mission ID.

- SendToCRM
  - Stores incoming CRM-oriented requests (for example, indicating which SI project IDs to pull and merge into CRM fields).

Both models are simple, immutable records of operations that enable auditing and replay in case of failures.

## Wrappers and drivers

- `SIWrapper` (in `api/SIWrapper.py`)
  - Responsible for authenticating with D-Tools SI and exposing methods like `create_project` and `get_project`.
  - Translates between the local field names and the SI API payloads.

- `CRMWrapper` (in `api/CRMWrapper.py`)
  - Handles Zoho OAuth/token management and exposes helpers like `get_deal`, `push_new_deal_data`, and `add_note`.

- `SQLDriver` (in `api/SQLDriver.py`)
  - Optional direct database helper for environments that use Microsoft SQL Server for additional bookkeeping. May require external DB drivers.

These wrappers centralize HTTP, logging, error handling, and rate-limit/backoff behaviors. They are the best place to adjust retry behavior and add metrics.

## Environment variables and configuration

The project uses `python-dotenv` to load runtime configuration from a `.env` file. Important variables (observed from wrapper usages and code comments) include:

- CRM related:
  - `CRM_ID`, `CRM_SECRET`, `CRM_SOID` (organization ID / scope values used by the Zoho integration)

- SI related:
  - `SI_TOKEN`, `SI_ENDPOINT`, or other SI auth details (used by `SIWrapper`)

- Optional SQL / server variables for `SQLDriver`:
  - `SQL_SERVER`, `SQL_USER`, `SQL_PASSWORD`, `SQL_DATABASE`

Other standard Django settings should be configured in `zohosi/settings.py` (SECRET_KEY, DATABASES, ALLOWED_HOSTS, etc.).

Note: The README intentionally omits specific installation and run commands per project constraints.

## Error handling and retries

- The current code persists inbound requests before performing external calls. This is a pragmatic design to ensure that requests are not lost if the external API call fails.
- Wrappers should implement robust retry/backoff and surface meaningful exceptions. Consider adding a background worker or task queue (e.g., Celery/RQ) for resilient retries if you need guaranteed delivery.

## Testing

- Unit tests live in `api/tests.py` and should exercise:
  - Serializer validation for expected shapes.
  - View behavior when creating `SendToSI`/`SendToCRM` objects (mocking wrapper clients).
  - Wrapper functionality where possible (mock external HTTP calls).

For integration tests, consider creating local fixtures for expected SI and CRM responses and use `pytest` with `pytest-django`.

## Security and privacy considerations

- API credentials and secrets must never be committed to source control. Use a `.env` file or environment-specific secret management.
- Review `zohosi/settings.py` for `DEBUG`, `ALLOWED_HOSTS`, and `SECRET_KEY` exposures before deploying to production.
- Rate-limiting and authentication are enforced at the DRF view layer (permission class `IsAuthenticated` is used) but ensure the authentication backend (token/session) is configured as needed.

## Observability suggestions

- Add structured logging in wrappers and views (request ids, correlation ids, durations).
- Emit metrics for: requests received, SI API failures, CRM API failures, and success counts.
- Add error notifications (email/slack) for repeated failures.

## Next steps and improvements

- Move long-running or retryable external calls into background tasks (Celery/RQ) to avoid blocking API responses.
- Add rate-limiting and per-user quotas to avoid accidental mass updates.
- Expand unit tests to cover wrapper behaviors using recorded HTTP fixtures (VCR-like approach) and add integration tests that run against a sandbox environment.

## License

Proprietary — for internal use only. See file headers for per-file copyright and author attributions.

## Contact

Author: Aidan Lelliott
Organization: Atlanta Soundworks
