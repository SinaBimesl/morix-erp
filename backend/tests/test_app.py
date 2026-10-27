from fastapi import FastAPI

from app.main import create_app


def test_create_app_returns_configured_app() -> None:
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "MorixERP"
    assert app.version == "0.1.0"


def test_create_app_returns_independent_instances() -> None:
    assert create_app() is not create_app()


def test_health_routes_registered(app: FastAPI) -> None:
    paths = set(app.openapi()["paths"])

    assert {"/health", "/health/db"} <= paths
