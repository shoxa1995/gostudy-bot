import os
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()

CLIENT_ID = os.getenv("CALENDLY_CLIENT_ID")
CLIENT_SECRET = os.getenv("CALENDLY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("CALENDLY_REDIRECT_URI")

# Step 1: Start Auth → Redirect to Calendly OAuth
@router.get("/auth/connect")
async def connect_to_calendly():
    calendly_auth_url = (
        "https://auth.calendly.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return RedirectResponse(calendly_auth_url)

# Step 2: Receive OAuth Callback and Exchange Code
@router.get("/auth/callback")
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}

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
        return {"error": "Failed to get access token", "details": token_res.text}

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    # 🔐 TODO: Save access_token securely in your database
    print("✅ Access Token Received:", access_token)

    return {"message": "Calendly connected successfully!", "access_token": access_token}
