import os
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.database import save_token  # ✅ Import save function

router = APIRouter()

CLIENT_ID = os.getenv("CALENDLY_CLIENT_ID")
CLIENT_SECRET = os.getenv("CALENDLY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("CALENDLY_REDIRECT_URI")

# ✅ Step 1: Redirect user to Calendly consent screen
@router.get("/auth/connect")
async def connect_to_calendly(request: Request):
    telegram_id = request.query_params.get("telegram_id")

    if not telegram_id:
        return {"error": "Missing Telegram ID in query string."}

    calendly_auth_url = (
        "https://auth.calendly.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&state={telegram_id}"  # Pass Telegram user ID via OAuth state
    )
    return RedirectResponse(calendly_auth_url)

# ✅ Step 2: Receive Calendly callback and save access_token
@router.get("/auth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # Telegram ID passed via `state`

    if not code or not state:
        return {"error": "Missing `code` or `state` (telegram_id)."}

    # Exchange the code for an access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://auth.calendly.com/oauth/token",
            json={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI
            },
            headers={"Content-Type": "application/json"}
        )

    if token_res.status_code != 200:
        return {
            "error": "Failed to get access token from Calendly.",
            "details": token_res.text
        }

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    # ✅ Save the access token with telegram_user_id
    telegram_user_id = int(state)
    await save_token(telegram_user_id, access_token)

    return {
        "message": "Calendly connected successfully!",
        "telegram_user_id": telegram_user_id,
        "access_token": access_token
    }
