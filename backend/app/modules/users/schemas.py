import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)

from app.modules.users.permissions import PERMISSIONS

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128  # bounds hashing cost per request


def _normalize(value: object) -> object:
    return value.strip().lower() if isinstance(value, str) else value


# Lowercased before the pattern check, so "Painter.One" is accepted as "painter.one".
Username = Annotated[
    str, BeforeValidator(_normalize), StringConstraints(pattern=r"^[a-z0-9][a-z0-9._-]{2,63}$")
]
Code = Annotated[
    str, BeforeValidator(_normalize), StringConstraints(pattern=r"^[a-z0-9][a-z0-9_-]{1,49}$")
]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Password = Annotated[
    str, StringConstraints(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
]
Email = Annotated[EmailStr, AfterValidator(str.lower)]


def _known_permissions(codes: list[str]) -> list[str]:
    unknown = sorted(set(codes) - PERMISSIONS.keys())
    if unknown:
        raise ValueError(f"unknown permissions: {', '.join(unknown)}")
    return sorted(set(codes))


PermissionCodes = Annotated[list[str], AfterValidator(_known_permissions)]


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WriteModel(BaseModel):
    """Request body. Unknown fields are rejected, not silently ignored."""

    model_config = ConfigDict(extra="forbid")


# --- auth ---------------------------------------------------------------


class LoginRequest(WriteModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]
    # Not length-checked beyond the maximum: old passwords may predate policy.
    password: Annotated[str, StringConstraints(max_length=PASSWORD_MAX_LENGTH)]


class ChangePasswordRequest(WriteModel):
    current_password: Annotated[str, StringConstraints(max_length=PASSWORD_MAX_LENGTH)]
    new_password: Password


# --- roles and permissions ----------------------------------------------


class PermissionRead(BaseModel):
    code: str
    description: str


class RoleSummary(ReadModel):
    id: uuid.UUID
    code: str
    name: str


class RoleRead(RoleSummary):
    description: str | None
    permissions: list[str]
    created_at: datetime
    updated_at: datetime


class RoleCreate(WriteModel):
    code: Code
    name: Name
    description: Description | None = None
    permissions: PermissionCodes = []


class RoleUpdate(WriteModel):
    name: Name | None = None
    description: Description | None = None
    permissions: PermissionCodes | None = None


# --- users --------------------------------------------------------------


class UserRead(ReadModel):
    id: uuid.UUID
    username: str
    email: str | None
    full_name: str
    job_title: str | None
    phone: str | None
    department_id: uuid.UUID | None
    is_active: bool
    is_superuser: bool
    must_change_password: bool
    locked_until: datetime | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    roles: list[RoleSummary]


class MeRead(UserRead):
    permissions: list[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: MeRead


class UserCreate(WriteModel):
    username: Username
    email: Email | None = None
    full_name: Name
    job_title: Name | None = None
    phone: Phone | None = None
    department_id: uuid.UUID | None = None
    password: Password
    is_superuser: bool = False
    # New accounts get a temporary password by default.
    must_change_password: bool = True
    role_ids: list[uuid.UUID] = []


class UserUpdate(WriteModel):
    """Only fields present in the request are changed; send null to clear."""

    email: Email | None = None
    full_name: Name | None = None
    job_title: Name | None = None
    phone: Phone | None = None
    department_id: uuid.UUID | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class ProfileUpdate(WriteModel):
    """Fields users may change on their own account; send null to clear."""

    email: Email | None = None
    full_name: Name | None = None
    phone: Phone | None = None


class PasswordReset(WriteModel):
    new_password: Password
    must_change_password: bool = True


class UserRolesUpdate(WriteModel):
    role_ids: list[uuid.UUID]


# --- organisation -------------------------------------------------------


class DepartmentRead(ReadModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    parent_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DepartmentCreate(WriteModel):
    code: Code
    name: Name
    description: Description | None = None
    parent_id: uuid.UUID | None = None


class DepartmentUpdate(WriteModel):
    name: Name | None = None
    description: Description | None = None
    parent_id: uuid.UUID | None = None
    is_active: bool | None = None


class TeamMemberRead(ReadModel):
    user_id: uuid.UUID
    is_lead: bool
    joined_at: datetime


class TeamRead(ReadModel):
    id: uuid.UUID
    department_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members: list[TeamMemberRead]


class TeamCreate(WriteModel):
    department_id: uuid.UUID
    name: Name
    description: Description | None = None


class TeamUpdate(WriteModel):
    department_id: uuid.UUID | None = None
    name: Name | None = None
    description: Description | None = None
    is_active: bool | None = None


class TeamMemberSet(WriteModel):
    is_lead: bool = False


# --- audit --------------------------------------------------------------


class AuditEventRead(ReadModel):
    id: uuid.UUID
    occurred_at: datetime
    actor_id: uuid.UUID | None
    action: str
    entity_type: str | None
    entity_id: str | None
    ip_address: str | None
    details: dict[str, Any] = Field(default_factory=dict)
