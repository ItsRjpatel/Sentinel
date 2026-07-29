import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import SuccessResponse, ErrorResponse
from app.core.security import create_access_token, verify_access_token
from app.core.exceptions import InvalidTokenError
from app.modules.auth.dependencies import get_db, oauth2_scheme
from app.modules.auth.models import User, RefreshToken
from app.modules.endpoints.models import Endpoint

router = APIRouter(tags=["endpoints"])

class EnrollRequest(BaseModel):
    hostname: str
    os_version: str
    hardware_hash: str
    mac_addresses: List[str] = Field(default_factory=list)
    ip_addresses: List[str] = Field(default_factory=list)

class EnrollData(BaseModel):
    agent_id: str
    access_token: str
    refresh_token: str
    heartbeat_interval_seconds: int

class HeartbeatRequest(BaseModel):
    status: str
    current_config_version: str
    timestamp: str
    metrics: dict

class HeartbeatData(BaseModel):
    config_revision: str
    config_payload: Optional[dict] = None
    command_pending: bool = False


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


@router.post("/endpoints/enroll", response_model=SuccessResponse[EnrollData])
async def enroll(data: EnrollRequest, db: AsyncSession = Depends(get_db)):
    # 1. Fetch system administrator user to link refresh token foreign keys
    stmt = select(User).where(User.username == "admin")
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        # Fallback to any active user if admin isn't registered yet
        res = await db.execute(select(User))
        user = res.scalars().first()
        if not user:
            raise HTTPException(status_code=500, detail="No system users available to host session.")

    # 2. Check if the physical hardware hash is already enrolled
    stmt = select(Endpoint).where(Endpoint.hardware_hash == data.hardware_hash)
    res = await db.execute(stmt)
    endpoint = res.scalar_one_or_none()

    if not endpoint:
        # Create a new endpoint record
        endpoint = Endpoint(
            hostname=data.hostname,
            os_version=data.os_version,
            hardware_hash=data.hardware_hash,
            mac_addresses=data.mac_addresses,
            ip_addresses=data.ip_addresses,
            status="healthy"
        )
        db.add(endpoint)
        await db.flush()

    # 3. Generate tokens using the Endpoint UUID as the subject
    access_token = create_access_token(
        subject=str(endpoint.id),
        username=endpoint.hostname,
        roles=[]
    )

    raw_refresh = secrets.token_hex(32)
    refresh_record = RefreshToken(
        token_hash=_hash_token(raw_refresh),
        expiry=datetime.now(timezone.utc) + timedelta(days=7),
        user_id=user.id,
        revoked=False
    )
    db.add(refresh_record)
    await db.commit()

    return SuccessResponse(
        message="Endpoint enrolled successfully",
        data=EnrollData(
            agent_id=str(endpoint.id),
            access_token=access_token,
            refresh_token=raw_refresh,
            heartbeat_interval_seconds=60
        )
    )


@router.post("/endpoints/heartbeat", response_model=SuccessResponse[HeartbeatData])
async def heartbeat(
    data: HeartbeatRequest,
    token: str = Depends(oauth2_scheme),
    x_agent_id: Optional[str] = Header(None, alias="X-Agent-ID"),
    db: AsyncSession = Depends(get_db)
):
    # Verify token signature and retrieve the Agent ID subject
    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    agent_id_str = payload.get("sub")
    if not agent_id_str:
        raise HTTPException(status_code=401, detail="Token missing subject identifier.")

    try:
        agent_id = uuid.UUID(agent_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid subject UUID format.")

    # Retrieve the endpoint from the database
    stmt = select(Endpoint).where(Endpoint.id == agent_id)
    res = await db.execute(stmt)
    endpoint = res.scalar_one_or_none()

    if not endpoint:
        raise HTTPException(status_code=401, detail="Enrolled endpoint not found.")

    # Update heartbeat telemetry timestamps
    endpoint.last_seen = datetime.now(timezone.utc)
    endpoint.status = data.status
    endpoint.config_version = data.current_config_version
    await db.commit()

    return SuccessResponse(
        message="Heartbeat accepted",
        data=HeartbeatData(
            config_revision=endpoint.config_version,
            config_payload=None,
            command_pending=False
        )
    )
