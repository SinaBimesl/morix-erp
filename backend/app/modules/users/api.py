from fastapi import APIRouter

from app.modules.users import routes_audit, routes_auth, routes_org, routes_roles, routes_users

router = APIRouter()
for module in (routes_auth, routes_users, routes_roles, routes_org, routes_audit):
    router.include_router(module.router)
