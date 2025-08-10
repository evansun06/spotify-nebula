import base64
import secrets
from fastapi import APIRouter
import os
import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

router = APIRouter(tags={'auth'})

@router.get("/login")
async def login():
    state = secrets.token_urlsafe(16)
    
    query_parameters = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
    }
    
    query_string = urlencode(query_parameters)
    auth_url = SPOTIFY_AUTHORIZE_URL + '?' + query_string
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str):
    body_parameters = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    client_creds_b64_str = client_creds_b64.decode()
    
    header_parameters = {
        'Authorization': f'Basic {client_creds_b64_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post("https://accounts.spotify.com/api/token", data=body_parameters, headers=header_parameters)

    return response.json()