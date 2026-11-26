import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import AwareDatetime
from sqlalchemy import select

from app.core.audit import AuditEvent
from app.core.db import SessionDep
from app.core.pagination import Page, PageParams, page_params
from app.modules.users.deps import Auth, require
from app.modules.users.permissions import AUDIT_READ
from app.modules.users.schemas import AuditEventRead
from app.modules.users.service import count

router = APIRouter(prefix="/audit-events", tags=["audit"])


@router.get("")
def list_audit_events(
    auth: Annotated[Auth, Depends(require(AUDIT_READ))],
    session: SessionDep,
    page: Annotated[PageParams, Depends(page_params)],
    actor_id: uuid.UUID | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    since: AwareDatetime | None = None,
    until: AwareDatetime | None = None,
) -> Page[AuditEventRead]:
    """Newest first."""
    stmt = select(AuditEvent).order_by(AuditEvent.occurred_at.desc(), AuditEvent.id)
    for column, value in (
        (AuditEvent.actor_id, actor_id),
        (AuditEvent.action, action),
        (AuditEvent.entity_type, entity_type),
        (AuditEvent.entity_id, entity_id),
    ):
        if value is not None:
            stmt = stmt.where(column == value)
    if since is not None:
        stmt = stmt.where(AuditEvent.occurred_at >= since)
    if until is not None:
        stmt = stmt.where(AuditEvent.occurred_at < until)
    events = session.scalars(stmt.limit(page.limit).offset(page.offset))
    return Page(
        items=[AuditEventRead.model_validate(e) for e in events],
        total=count(session, stmt),
        limit=page.limit,
        offset=page.offset,
    )
