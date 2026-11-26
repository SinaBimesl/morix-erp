from fastapi import FastAPI

from app.api import health
from app.modules.users.api import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="MorixERP",
        summary="Morix Guitar workshop management system API",
        version="0.6.0",
    )
    app.include_router(health.router)
    app.include_router(users_router, prefix="/api/v1")
    return app


app = create_app()
