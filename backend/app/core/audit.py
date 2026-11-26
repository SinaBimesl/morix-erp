"""Append-only audit log shared by all modules."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.db import Base, utcnow


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    # No foreign key: audit rows must outlive whatever they refer to.
    actor_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(64))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    details: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), default=dict
    )


def record(
    session: Session,
    action: str,
    *,
    actor_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: object = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEvent:
    """Add an audit event to the current transaction. Never put secrets in details."""
    event = AuditEvent(
        action=action,
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=None if entity_id is None else str(entity_id),
        ip_address=ip_address,
        details=details or {},
    )
    session.add(event)
    return event
