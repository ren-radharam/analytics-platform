import asyncio
import logging
import os
import uuid

import pandas as pd

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_events_batch(self, events_data: list[dict], org_id: str):
    """Process and persist a batch of events asynchronously."""

    async def _run():
        from app.db.session import AsyncSessionLocal
        from app.models.event import Event

        async with AsyncSessionLocal() as session:
            objs = [
                Event(
                    org_id=uuid.UUID(org_id),
                    event_name=e["event_name"],
                    properties=e.get("properties", {}),
                    source=e.get("source", "api"),
                )
                for e in events_data
            ]
            session.add_all(objs)
            await session.commit()
            logger.info("Persisted %s events for org %s", len(objs), org_id)

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc) from exc


@celery_app.task
def process_csv_upload(file_path: str, org_id: str):
    """Parse uploaded CSV and turn each row into an event."""
    df = pd.read_csv(file_path)
    events = []
    for _, row in df.iterrows():
        event_name = row.get("event_name", row.get("event", "csv_import"))
        props = {
            k: v
            for k, v in row.items()
            if k not in ("event_name", "event", "timestamp")
        }
        events.append(
            {"event_name": str(event_name), "properties": props, "source": "csv"},
        )
    if events:
        process_events_batch.delay(events, org_id)
    try:
        os.remove(file_path)
    except OSError:
        pass
