import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.api_key import APIKey
from app.models.user import User

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class APIKeyCreate(BaseModel):
    name: str


@router.post("/", status_code=201)
async def create_api_key(
    payload: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw_key, prefix = APIKey.generate()
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    ak = APIKey(
        name=payload.name,
        key_hash=key_hash,
        prefix=prefix,
        org_id=current_user.org_id,
    )
    db.add(ak)
    await db.commit()
    await db.refresh(ak)
    return {
        "id": str(ak.id),
        "name": ak.name,
        "key": raw_key,
        "prefix": prefix,
        "warning": "Store this key securely — it won't be shown again.",
    }


@router.get("/")
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where(APIKey.org_id == current_user.org_id),
    )
    return [
        {
            "id": str(k.id),
            "name": k.name,
            "prefix": k.prefix,
            "is_active": k.is_active,
        }
        for k in result.scalars()
    ]


@router.delete("/{key_id}")
async def revoke_key(
    key_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.org_id == current_user.org_id,
        ),
    )
    ak = result.scalar_one_or_none()
    if not ak:
        raise HTTPException(404, "Key not found")
    ak.is_active = False
    await db.commit()
    return {"message": "Key revoked"}
