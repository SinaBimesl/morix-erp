from fastapi import FastAPI

from app.api import health


def create_app() -> FastAPI:
    app = FastAPI(
        title="MorixERP",
        summary="Morix Guitar workshop management system API",
        version="0.1.0",
    )
    app.include_router(health.router)
    return app


app = create_app()
