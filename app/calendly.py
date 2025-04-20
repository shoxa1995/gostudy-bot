import os
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
SCHEDULING_LINK = os.getenv("CALENDLY_SCHEDULING_LINK")

headers = {
    "Authorization": f"Bearer {CALENDLY_API_KEY}",
    "Content-Type": "application/json",
}

async def get_available_slots():
    if not CALENDLY_API_KEY or not SCHEDULING_LINK:
        raise Exception("Calendly credentials are missing.")

    async with httpx.AsyncClient() as client:
        # ✅ STEP 1: Get current user’s URI
        user_res = await client.get("https://api.calendly.com/users/me", headers=headers)
        user_res.raise_for_status()
        user_uri = user_res.json()["resource"]["uri"]

        # ✅ STEP 2: Get event types for that user
        res = await client.get(
            f"https://api.calendly.com/event_types?user={user_uri}",
            headers=headers
        )
        res.raise_for_status()
        event_types = res.json().get("collection", [])

        event_uri = None
        for event in event_types:
            if event["scheduling_url"] == SCHEDULING_LINK:
                event_uri = event["uri"]
                break

        if not event_uri:
            raise Exception("Matching event type not found.")

        # ✅ STEP 3: Get availability for next 7 days
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(days=7)

        payload = {
            "event_type": event_uri,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "timezone": "Asia/Tashkent"
        }

        avail_res = await client.post(
            "https://api.calendly.com/availability",
            headers=headers,
            json=payload
        )
        avail_res.raise_for_status()
        slots = avail_res.json().get("collection", [])

        return [slot["start_time"].replace("T", " ").replace("Z", "") for slot in slots[:5]]
