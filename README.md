# MERP

Guitar workshop management system. This repository currently contains only the
backend core: configuration, database infrastructure, migrations, and a health
endpoint.

## Layout

```
compose.yaml          db (PostgreSQL 17) + backend, plus a "tests" profile
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
docker compose up -d --build                          # start db + backend
docker compose run --rm backend alembic upgrade head  # apply migrations
curl localhost:8000/health                            # liveness
curl localhost:8000/health/db                         # database connectivity
docker compose logs -f backend
docker compose down                                   # stop (data kept)
docker compose down -v                                # stop and delete database data
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
docker compose run --rm backend alembic upgrade head
```

The schema is managed only by Alembic; `create_all()` is not used.
