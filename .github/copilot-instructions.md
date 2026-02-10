<!-- Copilot / AI agent instructions for Onboarding-Boteco.pt (UPDATED) -->
# Copilot Instructions — Onboarding-Boteco.pt (UPDATED)

This file is an updated, concise guide for AI coding agents to be immediately productive in the repository. It supplements the existing `.github/copilot-instructions.md` with tighter examples and explicit run/debug/test commands.

## Big picture
- Reflex-based web app (UI pages + Reflex states) and an internal FastAPI app mounted on the same ASGI application (`app/app.py`).
- Clerk (via `reflex-clerk-api`) is used for authentication. Pages that must be protected use `on_load=clerk.protect` (examples in `app/app.py` are commented).
- Persistence uses Supabase via `app/services/supabase_client.py`. The code uses `postgrest`-style responses and a defensive `_execute` wrapper for error handling.
- Multi-tenant pattern: each organization gets its own Postgres schema named `org_{username}`. Provisioning is done by POSTing to the internal route `/api/provision_org` (see `app/api/provision.py`).

## Where to inspect first (fast tour)
- `app/app.py` — app bootstrap, theme, Clerk wrapping, page registration, and `app.api = api_app`.
- `app/states/onboarding_state.py` — main business flow for onboarding and the place to add validation & persistence logic.
- `app/services/supabase_client.py` — canonical Supabase usage: client init, upserts, rollback pattern, and `provision_schema` implementation.
- `app/api/provision.py` — FastAPI endpoint that runs a Supabase RPC (`execute_sql`) to create a schema. Uses the service role key.
- `app/pages/onboarding/` — UI steps implemented as Reflex components.
- `app/components/onboarding_stepper.py` and `app/utils/validators.py` — shared UI and validators.

## Concrete examples & patterns to reuse
- Registering pages and protecting routes (from `app/app.py`):

```py
app.add_page(dashboard, route="/app", on_load=clerk.protect)
```

- Supabase helper usage pattern (from `app/services/supabase_client.py`):
  - Use `create_client(url, key, options=ClientOptions(schema="reflex"))`.
  - Wrap calls in `_execute` to inspect `response.error` and raise helpful exceptions.
  - Example rollback: create boteco -> insert user_boteco; on failure delete the boteco.

- Provisioning pattern:
  - `SupabaseClient.provision_schema` posts to `http://localhost:8000/api/provision_org` with `{"boteco_username": "X"}`.
  - `app/api/provision.py` validates username against `^[a-zA-Z0-9_]+$` and runs `execute_sql` RPC to run DDL `CREATE SCHEMA IF NOT EXISTS "org_X";`.

## Dev & test commands (powershell)
- Install deps:

```powershell
pip install -r requirements.txt
```

- Run tests:

```powershell
pytest -q
```

- Run app locally (ASGI):

```powershell
uvicorn app.app:app --reload --port 8000
```

Notes:
- The provisioning endpoint is reachable at `http://localhost:8000/api/provision_org` when running uvicorn as above.
- The repo contains `load_env.py` which calls `dotenv.load_dotenv()` — place local credentials in a `.env` file.

## Environment variables (critical)
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` — service/admin key used by the provisioning endpoint (treat as extremely sensitive).
- `SUPABASE_KEY` — fallback (less privileged).
- `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`

Security: Do NOT store `SUPABASE_SERVICE_ROLE_KEY` in public CI logs or test fixtures. Ensure provisioning only runs against dev databases during local tests.

## Conventions & guidance for making changes
- Keep business logic in `app/states/*_state.py` as `rx.State` subclasses and expose async handlers with `@rx.event`.
- Use `supabase_client` helpers for DB operations — they centralize error handling and rollback semantics.
- When adding onboarding steps:
  1. Add the UI under `app/pages/onboarding/<step>.py`.
  2. Register the page in `app/app.py` with `app.add_page(...)`.
  3. Add any shared state fields / handlers in `app/states/onboarding_state.py`.
  4. Update `app/components/onboarding_stepper.py` if the step count changes.

## Gotchas & things to watch
- `SupabaseClient` default schema is `reflex`. Be explicit if you need to query public tables or other schemas.
- `provision_schema` uses a hardcoded `http://localhost:8000` endpoint — consider making this configurable via env var if deploying differently.
- Provisioning runs DDL (CREATE SCHEMA) via a service role key — avoid running against production by accident.

## Suggested small improvements (optional)
- Make the provisioning API URL configurable with an env var; fall back to `http://localhost:8000`.
- Add a short `CONTRIBUTING.md` with these run/test commands and how to supply test dev keys.
- Add an integration test that mocks the provisioning endpoint and verifies rollback behavior.

---
I created ` .github/COPILOT_INSTRUCTIONS_UPDATED.md` with these updates. If you'd like, I can:
- overwrite the original ` .github/copilot-instructions.md` with this content (confirm and I'll replace it),
- or apply a smaller patch that merges only selected sections into the existing file.

Which option do you prefer? If you want a direct replacement, I will update the original file now.
