import base64
import secrets
from fastapi import APIRouter, HTTPException
import os
import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
import requests
from src.database import crud, create_db

load_dotenv()

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

router = APIRouter(tags={'auth'})

def get_user_info(access_token: str):
    url = "https://api.spotify.com/v1/me"
    header = {"Authorization": f'Bearer {access_token}'}
    response = requests.get(url, headers=header)
    return response.json()

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
        token_data_response = await client.post("https://accounts.spotify.com/api/token", data=body_parameters, headers=header_parameters)
    
    token_data = token_data_response.json()
    
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    
    user_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(user_url, headers=headers)
    
    user_info = user_info_response.json()
    spotify_user_id = user_info.get('id')
    display_name = user_info.get('display_name')
    
    db_session = next(create_db.get_db())
    
    try:
        crud.create_nebula_user(db_session, spotify_user_id, display_name)
    except HTTPException:
        return {"message": "user already exists"}

    return {"message": "user successfully created"}