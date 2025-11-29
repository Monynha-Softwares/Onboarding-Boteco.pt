<!-- Copilot / AI agent instructions for Onboarding-Boteco.pt -->
# Copilot Instructions — Onboarding-Boteco.pt

Purpose: give an AI coding agent the minimum, actionable knowledge to be productive in this repo.

- **Big picture**
  - This is a Reflex-based web app (see `app/app.py`) that composes UI pages and registers an ASGI API.
  - Authentication is handled by `reflex-clerk-api` (Clerk). Protected pages are registered with `on_load=clerk.protect` (see onboarding routes in `app/app.py`).
  - Persistence and core business operations use Supabase via `app/services/supabase_client.py` and the `supabase` client library.
  - The repo uses a per-tenant schema provisioning model: the code provisions schemas named `org_{username}` by calling the internal FastAPI route `POST /api/provision_org` (see `app/api/provision.py` and `SupabaseClient.provision_schema`).

- **Where to look first (fast tour)**n+  - `app/app.py` — application entry, page & API registration, Clerk wrapping.
  - `app/pages/` — page components. Onboarding pages live in `app/pages/onboarding/` (personal, business, plan, payment, success).
  - `app/states/onboarding_state.py` — central onboarding flow state and Rx events. Key place for business logic (validation, submissions, calls to `supabase_client`).
  - `app/services/supabase_client.py` — DB helper, upsert/create patterns, provision API call, rollback logic.
  - `app/api/provision.py` — internal FastAPI endpoint that runs a Supabase RPC to create schemas. Uses service role key — treat as sensitive.
  - `app/components/onboarding_stepper.py` — UI pattern for multi-step flows (useful when adding steps).
  - `app/utils/validators.py` — input validation functions used by state handlers.
  - `alembic/` — DB migration tooling notes; see `alembic/README` for single-database config.

- **Data flow highlights / examples**
  - Personal -> Business -> Plan -> Payment: user input is stored via `OnboardingState` events. `handle_personal_submit` upserts the user in Supabase, sets `user_id`, then redirects to step 2.
  - Finalization (`handle_payment_submit`) creates `boteco` and `user_boteco` via `supabase_client.create_boteco_and_associate_user`, then triggers schema provisioning by POSTing to `/api/provision_org` on localhost (the internal API).
  - Provisioning is implemented as a server-side RPC call and will roll back DB records if provisioning fails — follow that pattern when adding transactional flows.

- **Dev & test workflows (discernible from repo)**
  - Install dependencies: `pip install -r requirements.txt`.
  - Run tests: `pytest` (there's a basic `tests/test_branding.py`).
  - Start a local server (example that works for ASGI apps in this layout):

    ```powershell
    pip install -r requirements.txt
    uvicorn app.app:app --reload --port 8000
    ```

    - The FastAPI internal route is reachable at `http://localhost:8000/api/provision_org` (used by `SupabaseClient.provision_schema`). If the team uses a different startup command (e.g., a Reflex dev server), verify before changing run scripts.

- **Environment & secrets**
  - Required env vars observed in code:
    - `SUPABASE_URL`
    - `SUPABASE_SERVICE_ROLE_KEY` (preferred for admin/provisioning) or `SUPABASE_KEY`
    - `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`
  - Treat `SUPABASE_SERVICE_ROLE_KEY` as extremely sensitive (used to run RPC/DDL).

- **Conventions & patterns specific to this project**
  - UI composition: pages use Reflex `rx.el` primitives and small helper functions (see `personal.py` and `business.py`), keep components pure and put shared UI in `app/components/`.
  - State & flow: central `OnboardingState` holds the multi-page flow; prefer adding fields and rx.event handlers there rather than scattering logic across pages.
  - API / service separation: internal FastAPI routes live under `app/api/` and are attached to the Reflex app via `app.api = api_app` in `app/app.py`.
  - DB safety: `supabase_client.py` shows the intended pattern: perform DB write(s), validate the response, and perform compensating deletes on error. Follow this for multi-step persistence.

- **When editing or extending onboarding**
  - Add page under `app/pages/onboarding/<step>.py` and register it in `app/app.py` with `app.add_page(...)`.
  - Update `OnboardingState` with new fields and event handlers; use `rx.event` for async interactions.
  - Update `onboarding_stepper` in `app/components/onboarding_stepper.py` if adding/removing steps (it computes progress bar width using `current_step`).

- **Common gotchas & safety checks**
  - Provisioning RPCs require the service role key and run DDL (CREATE SCHEMA). Ensure tests or local runs do not accidentally run provisioning against production.
  - `SupabaseClient._initialize_client` sets `schema="reflex"` by default; when acting on public tables or other schemas, be explicit about schema use.
  - The internal API is called via hardcoded `http://localhost:8000/api/provision_org` in `supabase_client.py` — change only if the dev server uses a different host/port or when adding environment-based overrides.

- **Examples you can use in PRs or code changes**
  - Add a protected page route:

    ```py
    from app.pages.onboarding.newstep import new_step
    app.add_page(new_step, route="/onboarding/step-5-extra", on_load=clerk.protect)
    ```

  - Call the internal provision API safely (follow `SupabaseClient.provision_schema`): use `httpx.AsyncClient`, call `POST /api/provision_org` with `{ "boteco_username": "username" }`, and handle HTTP errors.

- **If something is unclear**
  - Ask the maintainers: preferred run command (Reflex dev server vs. `uvicorn`), local dev Supabase setup, and any environment defaults.

Please review these instructions and tell me if you want the file more/less verbose, or if there are specific workflows (containers, Docker Compose, CI) to include.
