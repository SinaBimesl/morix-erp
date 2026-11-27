# MorixERP

Backend-first workshop management system for a guitar business: manufacturing,
sales, repairs, and related departments. The API title is "MorixERP"; the repo
and README still say "MERP".

## Working rules

- Read this file before planning or changing architecture.
- The architecture below is approved. Do not re-audit or redesign it unless
  there is a concrete defect or a new requirement.
- Do not modify `README.md` unless asked, or unless a command or workflow it
  documents becomes incorrect.
- Do not build frontend or new business modules without explicit approval.
- Work one approved step at a time. Run the relevant tests and report anything
  you could not verify.
- Do not commit unless explicitly asked.
- Before planning or building any business module, consult the business
  documents in `docs/` (below).

## Business documentation

The business source is `morix-erp.pdf` (repo root): a one-page Figma diagram,
mostly in Persian, of the business areas and their items. It has no processes
or data fields. It replaces `morix-comp-1.pdf`, which was the wrong file;
do not use that file or anything derived from it.

These documents transcribe the PDF:

- `docs/BUSINESS_REQUIREMENTS.md`: full transcription, areas, products and
  services, scope requirements with stable IDs (`BR-*`), open questions, and
  ambiguous terms.
- `docs/WORKFLOWS.md`: the process elements the PDF shows, such as maintenance
  tasks, repair services, and warranty coverage, with questions per area. No
  workflows are assumed.
- `docs/DOMAIN_MODEL.md`: Persian-English glossary, and the concepts and
  relationships the PDF shows. No entities or modules are proposed.

Rules:

- Statements are labelled **[PDF]** (source fact) or **[Interpretation]**
  (minimum reading of the diagram). The documents hold no assumptions.
- Before building on anything the PDF does not show, ask the user. If an
  assumption or recommendation is ever added, label it as such and never
  present it as a business fact.
- Use the glossary's English terms in code and the API.
- When the business answers an open question, update the documents and record
  where the answer came from.

## Architecture

Modular monolith, deployed with Docker Compose. No frontend for now.

- Python 3.13, dependencies managed only with `uv` (`backend/uv.lock` is committed)
- FastAPI
- SQLAlchemy 2.x, synchronous (`psycopg` 3 driver)
- Pydantic Settings for configuration
- PostgreSQL 17
- Alembic for all schema changes; `create_all()` is never used

## Layout

```
compose.yaml            db, backend; "migrate" and "tests" profiles
.env.example            template for .env
morix-erp.pdf           business source diagram (Persian)
docs/                   business requirements, workflows, domain model
backend/
  Dockerfile            base -> runtime / test stages, non-root "app" user
  alembic.ini
  app/main.py           create_app() factory
  app/core/config.py    Settings, get_settings()
  app/core/db.py        Base, UTCDateTime, utcnow, engine, get_session, SessionDep
  app/core/audit.py     AuditEvent model, audit.record()
  app/core/pagination.py  Page[T], page_params
  app/api/health.py     /health, /health/db
  app/modules/users/    User Manager (see below)
    models.py           tables
    permissions.py      permission catalog, define()
    security.py         Argon2 hashing, session tokens
    deps.py             CurrentAuth, require(): auth for every module's routes
    service.py          shared rules (escalation checks, 404/409 helpers)
    schemas.py          request (WriteModel) and response (ReadModel) bodies
    routes_*.py, api.py HTTP routes, mounted under /api/v1
    cli.py              create-superuser, prune-sessions
  migrations/           Alembic env and versions
  tests/                pytest, no external database needed
  tests/users/          User Manager tests on migrated SQLite
```

## Implemented (Core)

- Settings from environment variables with validation; `database_url` built with
  `URL.create`, so special characters in credentials are escaped.
- Engine and sessionmaker created lazily and cached. `pool_pre_ping=True`.
- `Base` with a fixed constraint naming convention so migrations stay stable.
- `GET /health` (liveness, no DB) and `GET /health/db` (readiness: `SELECT 1`,
  returns 503 if the database is unavailable).
- Database timeouts: connect timeout, app statement timeout, migration lock timeout.
- Compose: Postgres health check runs a real query over TCP; Postgres has no host
  port; backend binds to `127.0.0.1` by default.

## User Manager (implemented)

API under `/api/v1`; interactive docs at `/docs`.

- **Users** (`/users`): username login (lowercase, 3-64 chars of `a-z0-9._-`);
  email optional and unique, because shop-floor staff may have none. Profile
  fields, primary department, active flag, superuser flag. Users are never
  deleted, only deactivated, so history keeps its references.
- **Authentication** (`/auth`): `login`, `logout`, `me` (GET/PATCH own
  profile), `change-password`.
  - Passwords: Argon2id (`argon2-cffi` defaults), 12-128 characters, not equal
    to the username, no composition rules. Hashes are upgraded on login when
    the parameters change.
  - Sessions: opaque random bearer tokens (`Authorization: Bearer ...`). Only a
    SHA-256 hash is stored in `auth_sessions`. Chosen over JWT so logout,
    deactivation and password changes revoke access immediately.
  - Sessions expire after `AUTH_SESSION_HOURS`. Changing a password revokes the
    user's other sessions; an admin password reset or deactivation revokes all.
  - `AUTH_MAX_FAILED_LOGINS` consecutive failures lock the account for
    `AUTH_LOCKOUT_MINUTES`. Unknown user, wrong password, locked, and inactive
    all return the same 401 and take the same time.
  - Login failures are returned, not raised, so the failure count and audit
    event commit. This is the one intended exception to "errors roll back".
  - New users and admin resets set `must_change_password` by default; until
    changed, only `/auth/*` routes work.
- **Roles and permissions** (`/roles`, `/permissions`): RBAC. Permission codes
  are defined in code (`permissions.py`) and stored on roles as strings, so
  there is no permissions table to keep in sync. Unknown codes are rejected;
  codes later removed from code are ignored. Superusers hold every permission.
  Roles are global; department-scoped permissions are not implemented yet.
- **Escalation rules** (`service.py`), for anyone who is not a superuser:
  - only grant or remove permissions you hold (role edits, role assignment,
    role deletion);
  - only manage users whose permissions you hold, so a password reset cannot
    be used to take over a stronger account;
  - never create, manage or promote superusers.
  The last active superuser cannot be demoted or deactivated, and nobody can
  deactivate their own account.
- **Organisation** (`/departments`, `/teams`): departments form a tree via
  `parent_id`, with cycle checks. A department in use cannot be deleted;
  deactivate it instead. Teams belong to a department (name unique within it)
  and have members with an optional lead flag.
- **Audit log** (`/audit-events`, read-only): security and admin actions with
  actor, entity, IP and details. Kept in Core for all modules. Never store
  secrets in `details`.
- **Bootstrap**: create the first superuser with the CLI (password prompted):
  `docker compose run --rm backend python -m app.modules.users.cli create-superuser --username admin --full-name "Workshop Admin"`
  Prune old sessions periodically with `... cli prune-sessions` (default: older
  than 30 days).

Permissions: `users.read`, `users.manage`, `users.assign_roles`, `roles.read`,
`roles.manage`, `org.read`, `org.manage`, `audit.read`.

## Conventions for modules

- One package per module under `app/modules/<name>/`; mount its router in
  `app/main.py` under `/api/v1`, and import its models in `migrations/env.py`.
- Protect every route with `Depends(require(<permission>))` from
  `app.modules.users.deps`; define the module's permissions in its own
  `permissions.py` with `define()`.
- UUID primary keys. Annotate timestamps as `datetime`: `Base` maps them to
  `UTCDateTime`, which stores UTC and rejects naive values. Use `utcnow()`.
- Request bodies subclass a model with `extra="forbid"`; PATCH bodies apply only
  the fields sent (`service.changes()`), and `null` clears optional fields.
- Errors: 404 missing, 409 conflict or in-use, 422 invalid input or unknown
  reference, 403 missing permission. Check uniqueness first, then
  `flush_or_conflict()` to cover races.
- Record admin and security actions with `audit.record()`.
- Build response bodies inside the handler (`Read.model_validate(obj)`), while
  the session is open.

## Database sessions and transactions

- Endpoints get a session only through `SessionDep` from `app.core.db`.
- One session and one transaction per request: commit when the handler succeeds,
  roll back on any exception.
- `SessionDep` uses `Depends(get_session, scope="function")`, so the commit
  happens before the response is sent. A failed commit returns an error, never
  a success. Do not use plain `Depends(get_session)`.
- Handlers do not call `commit()` themselves.
- Sessions use `autoflush=False` and `expire_on_commit=False`.

## Configuration and secrets

- All configuration comes from environment variables via `Settings`; Compose
  loads them from `.env`.
- `.env` is never committed. `.env.example` holds placeholders only.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` are required.
- Optional: `ENVIRONMENT` (development/test/production), `POSTGRES_HOST`,
  `POSTGRES_PORT`, `DB_CONNECT_TIMEOUT` (5 s), `DB_STATEMENT_TIMEOUT_MS` (30000),
  `MIGRATION_LOCK_TIMEOUT_MS` (5000), `AUTH_SESSION_HOURS` (12),
  `AUTH_MAX_FAILED_LOGINS` (5), `AUTH_LOCKOUT_MINUTES` (15),
  `BACKEND_BIND_ADDRESS` (127.0.0.1), `BACKEND_PORT` (8000).
- `ENVIRONMENT` is validated and stored in `Settings.environment`, but no code
  reads it yet, so it currently has no functional effect.
- The password is a `SecretStr` and must never appear in logs, reprs, or URLs
  rendered as strings.
- The backend, migrate, and tests containers (built from `backend/Dockerfile`)
  run as the non-root `app` user. The `db` container uses the official
  PostgreSQL image and its own `postgres` user.

## Migrations

- Never run on app startup. Run only through the one-shot `migrate` service:
  `docker compose --profile migrate run --rm --build migrate`
- Models subclass `app.core.db.Base`; import their modules in
  `migrations/env.py` so autogenerate sees them.
- Create a revision with `migrations/` mounted and your own user, so the new
  file is written to the local working tree instead of being lost with the
  container:

  ```sh
  docker compose run --rm --user "$(id -u):$(id -g)" -v ./backend/migrations:/app/migrations \
    backend alembic revision --autogenerate -m "describe change"
  ```
- Generated revisions (`migrations/versions/`) are linted for real errors only
  (E/F/B; no line-length, UP or import-order rules) and are not formatted, so
  Alembic's template output passes as generated. Fix any finding before committing.
- Migrations must not import app code. `env.py` renders `UTCDateTime` as
  `sa.DateTime(timezone=True)`; check generated files for other app types.
- Online migrations use a lock timeout and no statement timeout. The whole
  upgrade runs in one transaction.
- `env.py` uses a connection passed in `config.attributes["connection"]` when
  present; tests use this to migrate SQLite.
- Production order: back up -> build -> review SQL -> migrate -> start the new
  app. Full steps are in `README.md`. Review the SQL with:
  `docker compose --profile migrate run --rm migrate alembic upgrade head --sql`
- Migrations must work with both the old and new app versions: add first,
  remove in a later release (expand, then contract).
- Prefer restoring a backup or a forward fix over `alembic downgrade`; use a
  downgrade only when it loses no data.

## Testing

```sh
cd backend && uv run pytest                          # local
docker compose --profile test run --rm --build tests # in Docker
cd backend && uv lock --check                        # lockfile matches pyproject
cd backend && uv run ruff check . && uv run ruff format --check .  # lint, format
```

Ruff is a dev dependency and is configured in `backend/pyproject.toml`: line
length 100, rules E, F, UP, B, I. Run `uv run ruff format .` and
`uv run ruff check --fix .` before finishing a change.

Tests need no external database: they set their own environment in
`tests/conftest.py`, use SQLite or mocks for sessions, and use a silent local
socket for timeouts. User Manager tests build an in-memory SQLite schema by
running the real migrations (`tests/users/conftest.py`), use cheap Argon2
parameters, and `test_schema.py` fails if models and migrations drift apart.
Add a regression test with each bug fix.

## Current limitations

Not yet verified, because Docker was not available:

- Image builds, `docker compose up`, and the `migrate` and `tests` profiles.
- The Postgres health check on a fresh volume.
- That the backend port is reachable only on `127.0.0.1` by default.
- Behaviour against real PostgreSQL: migrations, `statement_timeout`, and
  `lock_timeout` enforcement.
- The `pg_dump` backup command in `README.md`.
- User Manager on real PostgreSQL: the migration, `JSONB`, and the row lock
  (`SELECT ... FOR UPDATE`) that keeps failed-login counts correct under
  concurrent attempts. Tests run on SQLite only.

User Manager limits (deliberate, for later):

- No per-IP rate limiting; lockout is per account, so an attacker can lock out
  a known username. Put rate limiting at the reverse proxy.
- Audit and session IPs are the direct peer; behind a proxy they are the
  proxy's address until forwarded headers are trusted explicitly.
- No MFA, no email-based password reset, no API keys for machines.
- Roles are global; no per-department data scoping yet.
- No retention policy for the audit log; it grows with every login attempt.

## Roadmap

1. Finish and verify Core, including the Docker and PostgreSQL checks above.
2. User Manager: implemented (above). Verify on real PostgreSQL.
3. Business modules (manufacturing, sales, repairs, ...) later, each as a
   module under `app/modules/`.
