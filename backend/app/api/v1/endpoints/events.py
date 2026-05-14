import hashlib
import os
import tempfile
import uuid

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.api_key import APIKey
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventBatch, EventIn, EventOut
from app.workers.tasks import process_csv_upload, process_events_batch

router = APIRouter(prefix="/events", tags=["events"])


async def get_org_from_api_key(request: Request, db: AsyncSession) -> uuid.UUID:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(401, "API key required")
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active.is_(True),
        ),
    )
    ak = result.scalar_one_or_none()
    if not ak:
        raise HTTPException(401, "Invalid API key")
    return ak.org_id


@router.post("/ingest", status_code=202)
async def ingest_event(
    event: EventIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    org_id = await get_org_from_api_key(request, db)
    process_events_batch.delay([event.model_dump(mode="json")], str(org_id))
    return {"accepted": 1}


@router.post("/ingest/batch", status_code=202)
async def ingest_batch(
    payload: EventBatch,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    org_id = await get_org_from_api_key(request, db)
    events = [e.model_dump(mode="json") for e in payload.events]
    process_events_batch.delay(events, str(org_id))
    return {"accepted": len(events)}


@router.post("/upload/csv", status_code=202)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files allowed")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    tmp_path = tmp.name
    tmp.close()
    content = await file.read()
    async with aiofiles.open(tmp_path, "wb") as f:
        await f.write(content)
    process_csv_upload.delay(tmp_path, str(current_user.org_id))
    return {"message": "CSV queued for processing", "filename": file.filename}


@router.get("/", response_model=list[EventOut])
async def list_events(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event)
        .where(Event.org_id == current_user.org_id)
        .order_by(Event.timestamp.desc())
        .limit(limit)
        .offset(offset),
    )
    return result.scalars().all()


@router.get("/stats")
async def event_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total = await db.execute(
        select(func.count())
        .select_from(Event)
        .where(Event.org_id == current_user.org_id),
    )
    by_name = await db.execute(
        select(Event.event_name, func.count().label("count"))
        .where(Event.org_id == current_user.org_id)
        .group_by(Event.event_name)
        .order_by(func.count().desc())
        .limit(10),
    )
    return {
        "total_events": total.scalar(),
        "top_events": [{"name": r[0], "count": r[1]} for r in by_name],
    }
