# MERP

Guitar workshop management system. This repository currently contains only the
backend core: configuration, database infrastructure, migrations, and a health
endpoint.

## Layout

```
compose.yaml          db (PostgreSQL 17) + backend, plus "migrate" and "tests" profiles
backend/
  app/main.py         create_app() factory
  app/core/           configuration (config.py) and database (db.py)
  app/api/            HTTP routes (health)
  app/modules/        future business modules
  migrations/         Alembic
  tests/              pytest (no database needed)
```

## Setup

Requires Docker with the Compose plugin.

```sh
cp .env.example .env   # then set a real POSTGRES_PASSWORD
```

## Run

```sh
docker compose --profile migrate run --rm --build migrate  # apply migrations
docker compose up -d --build                               # start db + backend
curl localhost:8000/health                                 # liveness
curl localhost:8000/health/db                              # database connectivity
docker compose logs -f backend
docker compose down                                        # stop (data kept)
docker compose down -v                                     # stop and delete database data
```

API docs: http://localhost:8000/docs

## Test

```sh
docker compose --profile test run --rm --build tests
```

Locally without Docker (requires [uv](https://docs.astral.sh/uv/)):

```sh
cd backend && uv run pytest
```

## Dependencies

Managed with uv only; `backend/uv.lock` is committed.

```sh
cd backend
uv add <package>          # runtime dependency
uv add --dev <package>    # test/dev dependency
```

## Migrations

Models subclass `app.core.db.Base`; import their modules in
`migrations/env.py` so autogenerate sees them.

```sh
# mount migrations/ so the new revision file lands in your working copy
docker compose run --rm --user "$(id -u):$(id -g)" -v ./backend/migrations:/app/migrations \
  backend alembic revision --autogenerate -m "describe change"
docker compose --profile migrate run --rm --build migrate
```

The schema is managed only by Alembic; `create_all()` is not used. The app
never migrates on startup; migrations run only through the `migrate` service.

### Production deploy

1. **Back up** the database:
   `docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' > backup.dump`
2. **Build** the new image: `docker compose --profile migrate build backend migrate`
3. **Review** the SQL that will run:
   `docker compose --profile migrate run --rm migrate alembic upgrade head --sql`
4. **Migrate**: `docker compose --profile migrate run --rm migrate`.
   The whole upgrade runs in one transaction; on failure nothing is applied.
5. **Deploy** the app only after step 4 succeeds: `docker compose up -d backend`

The old app keeps running during step 4, so each migration must be compatible
with both versions: add columns/tables first, and remove old ones in a later
release (expand, then contract).

If a migration fails with `lock timeout`, a long transaction held the table;
it rolled back cleanly, so retry later (`MIGRATION_LOCK_TIMEOUT_MS`, default
5000). To undo a release, prefer restoring the backup or shipping a forward
fix; use `alembic downgrade` only when its downgrade loses no data.
