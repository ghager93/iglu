import os
import json
from datetime import datetime, timezone
import httpx
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

HOST_URL = os.getenv("HOST_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USER_ID = os.getenv("USER_ID")

TOKEN_ENDPOINT = "auth/login"
GLUCOSE_ENDPOINT = f"connections/{USER_ID}/graph"
TOKEN_FILE = "token.json"


def save_token(token: str, expiry: int):
    data = {"access_token": token, "expiry": expiry}
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)


def load_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
        if datetime.now().timestamp() > data.get("expiry", 0):
            return None
        return data.get("access_token")


async def get_token():
    token = load_token()
    if token:
        return token
    url = f"{HOST_URL.rstrip('/')}/{TOKEN_ENDPOINT.lstrip('/')}"
    headers = {"Content-Type": "application/json", "version": "4.7.0", "product": "llu.android"}
    payload = {"email": USERNAME, "password": PASSWORD}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    token = data.get("data", {}).get("authTicket", {}).get("token", None)
    if not token:
        raise ValueError("Failed to retrieve token from response")
    expiry = data.get("data", {}).get("authTicket", {}).get("expires", None)
    if not expiry:
        expiry = int(datetime.now().timestamp()) + 24 * 60 * 60
    save_token(token, expiry)
    return token


async def fetch_glucose_readings(token: str):
    url = f"{HOST_URL.rstrip('/')}/{GLUCOSE_ENDPOINT.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}", "version": "4.7.0", "product": "llu.android"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return extract_readings(resp.json())


def extract_readings(api_resp):
    """Return list of readings with 'value' and epoch 'timestamp' from API response."""
    data = api_resp.get('data', {})
    graph = data.get('graphData', [])
    current_measurement = data.get("connection", {}).get("glucoseMeasurement", {})
    if current_measurement:
        # add current measurement to the beginning of the list
        graph.append(current_measurement)
    readings = []
    for item in graph:
        ts_str = item.get('Timestamp')
        # parse month/day/year time with AM/PM
        dt = datetime.strptime(ts_str, '%m/%d/%Y %I:%M:%S %p')
        # assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
        ts = int(dt.timestamp())
        readings.append({'value': item.get('Value'), 'timestamp': ts})
    return readings


async def main():
    token = await get_token()
    logger.debug(f"Token: {token}")
    readings = await fetch_glucose_readings(token)
    print(json.dumps(readings, indent=2))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
