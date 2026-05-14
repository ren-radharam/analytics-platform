import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.dashboard import Dashboard, Widget
from app.models.user import User
from app.schemas.dashboard import DashboardCreate, DashboardOut, WidgetCreate, WidgetOut

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("/", response_model=DashboardOut, status_code=201)
async def create_dashboard(
    payload: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    d = Dashboard(
        **payload.model_dump(),
        org_id=current_user.org_id,
        owner_id=current_user.id,
    )
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return d


@router.get("/", response_model=list[DashboardOut])
async def list_dashboards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dashboard).where(Dashboard.org_id == current_user.org_id),
    )
    return result.scalars().all()


@router.get("/{dashboard_id}")
async def get_dashboard(
    dashboard_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.org_id == current_user.org_id,
        ),
    )
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(404, "Dashboard not found")
    widgets_result = await db.execute(
        select(Widget).where(Widget.dashboard_id == dashboard_id),
    )
    widgets = [
        WidgetOut.model_validate(w).model_dump()
        for w in widgets_result.scalars()
    ]
    return {
        **DashboardOut.model_validate(d).model_dump(),
        "widgets": widgets,
    }


@router.delete("/{dashboard_id}", status_code=204)
async def delete_dashboard(
    dashboard_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.org_id == current_user.org_id,
        ),
    )
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(404, "Dashboard not found")
    await db.delete(d)
    await db.commit()


@router.post("/{dashboard_id}/widgets", response_model=WidgetOut, status_code=201)
async def add_widget(
    dashboard_id: uuid.UUID,
    payload: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.org_id == current_user.org_id,
        ),
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Dashboard not found")
    w = Widget(**payload.model_dump(), dashboard_id=dashboard_id)
    db.add(w)
    await db.commit()
    await db.refresh(w)
    return w


@router.delete("/{dashboard_id}/widgets/{widget_id}", status_code=204)
async def remove_widget(
    dashboard_id: uuid.UUID,
    widget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Widget).where(
            Widget.id == widget_id,
            Widget.dashboard_id == dashboard_id,
        ),
    )
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, "Widget not found")
    await db.delete(w)
    await db.commit()
