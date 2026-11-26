"""Permission catalog.

Permissions are defined in code because code enforces them. Roles store the
codes; each module defines its own with `define()` at import time.
"""

PERMISSIONS: dict[str, str] = {}


def define(code: str, description: str) -> str:
    if code in PERMISSIONS:
        raise ValueError(f"permission already defined: {code}")
    PERMISSIONS[code] = description
    return code


USERS_READ = define("users.read", "View users")
USERS_MANAGE = define("users.manage", "Create, update, deactivate users and reset passwords")
USERS_ASSIGN_ROLES = define("users.assign_roles", "Assign roles to users")
ROLES_READ = define("roles.read", "View roles and the permission catalog")
ROLES_MANAGE = define("roles.manage", "Create, update and delete roles")
ORG_READ = define("org.read", "View departments and teams")
ORG_MANAGE = define("org.manage", "Manage departments, teams and team members")
AUDIT_READ = define("audit.read", "View the audit log")
