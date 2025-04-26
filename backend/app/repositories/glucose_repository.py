from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.glucose_reading import GlucoseReading as GlucoseReadingModel

async def fetch_readings(
    session: AsyncSession,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None
) -> List[GlucoseReadingModel]:
    stmt = select(GlucoseReadingModel)
    if from_ts is not None:
        stmt = stmt.filter(GlucoseReadingModel.timestamp >= from_ts)
    if to_ts is not None:
        stmt = stmt.filter(GlucoseReadingModel.timestamp <= to_ts)
    stmt = stmt.offset(skip)
    # if limit is not None:
    #     stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

async def fetch_latest(
    session: AsyncSession
) -> Optional[GlucoseReadingModel]:
    stmt = select(GlucoseReadingModel).order_by(GlucoseReadingModel.timestamp.desc()).limit(1)
    result = await session.execute(stmt)
    return result.scalars().first()

async def upsert_readings(
    session: AsyncSession,
    readings_data: List[dict]
) -> None:
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    stmt = sqlite_insert(GlucoseReadingModel).values(readings_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["timestamp"],
        set_={"value": stmt.excluded["value"]}
    )
    await session.execute(stmt)
    await session.commit()

async def delete_readings(
    session: AsyncSession,
    ids: Optional[List[int]] = None,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None
) -> List[GlucoseReadingModel]:
    query = await fetch_readings(session, from_ts, to_ts)
    if ids:
        query = [r for r in query if r.id in ids]
    for r in query:
        await session.delete(r)
    await session.commit()
    return query