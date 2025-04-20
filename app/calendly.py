import httpx
from datetime import datetime, timedelta
from typing import List

# ✅ Fetch real-time availability from Calendly using OAuth token
async def get_user_slots(access_token: str) -> List[str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Get user's event types (Calendly meetings)
    async with httpx.AsyncClient() as client:
        event_type_res = await client.get(
            "https://api.calendly.com/event_types",
            headers=headers
        )

    if event_type_res.status_code != 200:
        raise Exception(f"Failed to fetch event types: {event_type_res.text}")

    event_types = event_type_res.json().get("collection", [])
    if not event_types:
        raise Exception("No event types found for this Calendly account.")

    # Use the first event_type found (or implement custom selector)
    event_uri = event_types[0]["uri"]

    # Step 2: Define availability window (next 7 days)
    start = datetime.utcnow()
    end = start + timedelta(days=7)

    payload = {
        "event_type": event_uri,
        "start_time": start.isoformat() + "Z",
        "end_time": end.isoformat() + "Z",
        "timezone": "Asia/Tashkent"
    }

    # Step 3: Query Calendly availability
    async with httpx.AsyncClient() as client:
        avail_res = await client.post(
            "https://api.calendly.com/availability",
            headers=headers,
            json=payload
        )

    if avail_res.status_code != 200:
        raise Exception(f"Failed to fetch availability: {avail_res.text}")

    slots = avail_res.json().get("collection", [])
    if not slots:
        return []

    # Step 4: Format time strings nicely for Telegram display
    return [
        slot["start_time"]
        .replace("T", " ")
        .replace("Z", "")
        for slot in slots[:5]
    ]
