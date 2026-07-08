# Multi-Tenant Robot Control Guide

**Load this when:** Implementing tenant isolation for multiple RoboMaster users/groups sharing the same backend.

---

## Overall Pattern

Tenant-per-organization model where each tenant owns isolated robot fleets. Users authenticate via JWT with tenant claims, access is enforced at the service layer.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   User A    │────▶│  Tenant X    │────▶│ Robot X-1   │
│  (Member)   │     │  Organization│     │  Robot X-2  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
┌─────────────┐     ┌────┴─────────┐     ┌─────────────┐
│   User B    │────▶│  Tenant Y    │────▶│ Robot Y-1   │
│   (Admin)   │     │  Organization│     └─────────────┘
└─────────────┘     └──────────────┘
```

---

## Step 1: Define Tenant-Aware Models

Store tenant ID on all tenant-scoped entities. Use Pydantic validators for isolation checks.

```python
# backend/app/models/tenant.py
from pydantic import BaseModel, Field
from uuid import UUID

class Tenant(BaseModel):
    """Organization entity isolating robot fleets."""
    id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    max_robots: int = Field(default=5, ge=1, le=50)
    max_users: int = Field(default=10, ge=1, le=100)

class TenantUser(BaseModel):
    """User membership within a tenant."""
    user_id: UUID
    tenant_id: UUID
    role: str = Field(..., pattern="^(admin|operator|viewer)$")
    granted_at: datetime

class Robot(BaseModel):
    """Robot entity scoped to single tenant."""
    id: UUID
    tenant_id: UUID  # Isolation boundary
    name: str = Field(..., min_length=1, max_length=50)
    serial_number: str = Field(..., pattern="^\\d{10,20}$")
    max_speed_mps: float = Field(default=0.5, le=2.0)
    is_active: bool = True
```

**Rules:**
- Every tenant-scoped model MUST have `tenant_id: UUID`
- Never allow cross-tenant queries without explicit `tenant_id` filter
- Validate tenant limits (max_robots, max_users) at service layer

---

## Step 2: Implement Tenant Context Dependency

Extract tenant from JWT claims and inject into all service calls.

```python
# backend/app/core/tenant.py
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

class TenantContext(BaseModel):
    tenant_id: UUID
    user_id: UUID
    role: str

async def require_tenant_context(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> TenantContext:
    """Extract tenant claims from JWT."""
    payload = verify_jwt(token)
    tenant_id = payload.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(403, "No tenant assignment")
    
    # Validate user still belongs to tenant
    membership = await get_membership(payload["sub"], tenant_id)
    if not membership:
        raise HTTPException(403, "Tenant access revoked")
    
    return TenantContext(
        tenant_id=UUID(tenant_id),
        user_id=UUID(payload["sub"]),
        role=membership.role
    )

# Usage in router
@router.post("/robots", response_model=RobotResponse)
async def create_robot(
    cmd: CreateRobotCommand,
    tenant: TenantContext = Depends(require_tenant_context)
) -> RobotResponse:
    robot = await robot_service.create_robot(cmd, tenant)
    return RobotResponse.from_model(robot)
```

**Rules:**
- All protected routes MUST use `require_tenant_context` dependency
- Verify tenant membership on every request (not just token validity)
- Pass `TenantContext` to all service methods, don't extract again

---

## Step 3: Enforce Isolation in Services

Filter all queries by tenant_id. Raise 404 (not 403) for cross-tenant access attempts to prevent ID enumeration.

```python
# backend/app/services/robot_service.py
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_robot(
    cmd: CreateRobotCommand,
    tenant: TenantContext
) -> Robot:
    """Create robot within tenant boundaries."""
    # Check tenant limits
    current_count = await db.robots.count(
        {"tenant_id": tenant.tenant_id, "is_active": True}
    )
    tenant_config = await db.tenants.find_one({"id": tenant.tenant_id})
    
    if current_count >= tenant_config.max_robots:
        raise HTTPException(400, f"Robot limit ({tenant_config.max_robots}) reached")
    
    robot = Robot(
        id=uuid4(),
        tenant_id=tenant.tenant_id,  # Force from context
        name=cmd.name,
        serial_number=cmd.serial_number
    )
    
    await db.robots.insert_one(robot.model_dump())
    logger.info("robot_created", robot_id=str(robot.id), tenant_id=str(tenant.tenant_id))
    return robot

async def get_robot(
    robot_id: UUID,
    tenant: TenantContext
) -> Robot:
    """Get robot ONLY if belongs to tenant."""
    robot = await db.robots.find_one({
        "id": robot_id,
        "tenant_id": tenant.tenant_id  # Isolation enforced here
    })
    
    if not robot:
        # Return 404 to prevent ID enumeration across tenants
        raise HTTPException(404, "Robot not found")
    
    return Robot(**robot)

async def execute_robot_command(
    robot_id: UUID,
    command: MoveCommand,
    tenant: TenantContext
) -> str:
    """Execute command with tenant isolation + safety checks."""
    # Tenant isolation
    robot = await get_robot(robot_id, tenant)
    
    # RBAC: Only admin/operator can move
    if tenant.role not in ("admin", "operator"):
        raise HTTPException(403, "Insufficient permissions")
    
    # Tenant-specific speed limit (capped at global 0.5 m/s)
    max_speed = min(robot.max_speed_mps, 0.5)
    if command.speed > max_speed:
        raise HTTPException(400, f"Speed exceeds tenant limit ({max_speed} m/s)")
    
    # Execute via robot-bridge
    return await robot_bridge.move(robot.serial_number, command)
```

**Rules:**
- Every database query MUST include `tenant_id` filter
- Return 404 (not 403) for "not found" to hide cross-tenant existence
- Log all cross-tenant access attempts as security events
- Enforce RBAC after tenant isolation (defense in depth)

---

## Step 4: Add Tenant-Aware Agent Tools

Pydantic AI tools must validate tenant context before robot control.

```python
# backend/app/agents/robot_agent.py
from pydantic_ai import Agent, RunContext
from app.core.tenant import TenantContext

@robot_agent.tool
async def move_forward(
    ctx: RunContext[AgentDependencies],
    robot_id: str,
    distance_mm: int = Field(..., ge=0, le=5000),
    speed: float = Field(..., ge=0.0, le=0.5),
) -> str:
    """Move robot forward within tenant boundaries.
    
    Use this when you need to:
    - Navigate to target position
    - Move robot in straight line
    
    Do NOT use for:
    - Cross-tenant robot access (enforced automatically)
    - Emergency stops (use emergency_stop)
    
    Args:
        robot_id: UUID of robot (must belong to user's tenant)
        distance_mm: Distance in millimeters (0-5000)
        speed: Speed in m/s (capped at tenant limit)
    """
    tenant = ctx.deps.tenant_context
    
    try:
        robot_uuid = UUID(robot_id)
    except ValueError:
        return "Invalid robot_id format"
    
    # Service enforces tenant isolation + RBAC
    cmd = MoveCommand(distance_mm=distance_mm, speed=speed)
    
    try:
        result = await robot_service.execute_robot_command(
            robot_uuid, cmd, tenant
        )
        return f"Moved {distance_mm}mm at {speed}m/s"
    except HTTPException as e:
        if e.status_code == 404:
            return "Robot not found or not in your organization"
        if e.status_code == 403:
            return "You don't have permission to control this robot"
        raise
```

**Rules:**
- Pass `TenantContext` through agent deps, not tool params
- Handle 404/403 from service layer with user-friendly messages
- Never expose raw UUIDs or internal error details

---

## Quick Checklist

- [ ] Add `tenant_id: UUID` to all tenant-scoped models
- [ ] Create `TenantContext` dependency extracting JWT claims
- [ ] Implement `require_tenant_context` on all protected routes
- [ ] Filter ALL database queries by `tenant_id`
- [ ] Return 404 (not 403) for cross-tenant access attempts
- [ ] Enforce tenant limits (max_robots, max_users) in services
- [ ] Add RBAC checks after tenant isolation
- [ ] Log all cross-tenant access attempts as security events
- [ ] Pass `TenantContext` through agent deps
- [ ] Test tenant isolation: User A should never see User B's robots
