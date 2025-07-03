from typing import List, Optional

import fetch_glucose
from app.models.glucose_reading import GlucoseReading as GlucoseReadingModel
from app.repositories.glucose_repository import (
    delete_readings,
    fetch_latest,
    fetch_readings,
    upsert_readings,
)
from app.schemas.glucose_reading import GlucoseReadingCreate, RemoteReading
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def get_glucose_readings(
    session: AsyncSession,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None
) -> List[GlucoseReadingModel]:
    return await fetch_readings(session, from_ts, to_ts, skip, limit)

async def create_glucose_reading(
    session: AsyncSession,
    reading: GlucoseReadingCreate
) -> GlucoseReadingModel:
    model = GlucoseReadingModel(value=reading.value, timestamp=reading.timestamp)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model

async def create_bulk_readings(
    session: AsyncSession,
    readings: List[GlucoseReadingCreate],
    format: str = "json"
) -> List[GlucoseReadingModel]:
    data = [dict(value=r.value, timestamp=r.timestamp) for r in readings]
    await upsert_readings(session, data)
    # fetch and return updated entities
    return await fetch_readings(session)

async def fetch_and_save_remote(
    session: AsyncSession
) -> List[RemoteReading]:
    logger.debug("Service: fetching remote readings")
    token = await fetch_glucose.get_token()
    readings = await fetch_glucose.fetch_glucose_readings(token)
    data = [dict(value=r["value"], timestamp=r["timestamp"]) for r in readings]
    if data:
        await upsert_readings(session, data)
    logger.info(f"Service: fetched and saved {len(readings)} remote readings")
    return readings

async def delete_glucose_readings(
    session: AsyncSession,
    ids: Optional[List[int]] = None,
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None
) -> List[GlucoseReadingModel]:
    return await delete_readings(session, ids, from_ts, to_ts)

async def export_glucose_readings(
    session: AsyncSession,
    format: str = "json",
    from_ts: Optional[int] = None,
    to_ts: Optional[int] = None,
    skip: int = 0,
    limit: Optional[int] = None
):
    readings = await fetch_readings(session, from_ts, to_ts, skip, limit)
    if format == "json":
        return [r.__dict__ for r in readings]
    # CSV/HTML export logic to be implemented elsewhere
    if format == "csv":
        from datetime import datetime
        
        header = "ID,Glucose Value (mmol/L),Timestamp,Formatted Time\n"
        rows = []
        for r in readings:
            dt = datetime.fromtimestamp(r.timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            rows.append(f"{r.id},{r.value},{r.timestamp},{formatted_time}")
        return header + "\n".join(rows)
    if format == "html":
        from datetime import datetime

        # Create table rows with formatted timestamp
        table_rows = ""
        for r in readings:
            # Convert epoch timestamp to readable format
            dt = datetime.fromtimestamp(r.timestamp)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # Color code the glucose value
            value_color = "black"
            if r.value < 3.9:
                value_color = "red"  # Low
            elif r.value > 10.0:
                value_color = "orange"  # High
            elif 3.9 <= r.value <= 7.8:
                value_color = "green"  # Normal
            
            table_rows += f"""
            <tr>
                <td>{r.id}</td>
                <td style="color: {value_color}; font-weight: bold;">{r.value} mmol/L</td>
                <td>{formatted_time}</td>
            </tr>
            """
        
        html_export = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Glucose Readings Export</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background-color: white;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #e8f5e8;
                }}
                .summary {{
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #e8f5e8;
                    border-radius: 5px;
                }}
                .timestamp {{
                    color: #666;
                    font-size: 0.9em;
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Glucose Readings Report</h1>
                
                <div class="summary">
                    <strong>Summary:</strong> {len(readings)} readings exported
                    {f" (from {datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d %H:%M:%S') if from_ts else 'beginning'} to {datetime.fromtimestamp(to_ts).strftime('%Y-%m-%d %H:%M:%S') if to_ts else 'now'})" if from_ts or to_ts else ""}
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Glucose Value</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                
                <div class="timestamp">
                    Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        return html_export
    raise ValueError("Unsupported format")

async def get_latest_glucose_reading(
    session: AsyncSession
) -> Optional[GlucoseReadingModel]:
    return await fetch_latest(session)
