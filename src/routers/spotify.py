import base64
from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Security
import os
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
from src.database.models import NebulaUser
from src.database import crud, create_db
from jose import JWTError, jwt
from starlette import status

load_dotenv()

SPOTIFY_AUTHORIZE_BASE_URL = "https://accounts.spotify.com"
SPOTIFY_CALL_BASE_URL = "https://api.spotify.com/v1/me"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
B64_HEADER = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
TOKEN_REQUEST_HEADERS = {'Authorization': f'Basic {B64_HEADER}',
                        'Content-Type': 'application/x-www-form-urlencoded'}

oauth2_scheme = HTTPBearer()
router = APIRouter(tags={'auth'})
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

async def get_user_info(access_token: str):
    header = {"Authorization": f'Bearer {access_token}'}
    async with httpx.AsyncClient() as client:
        response = await client.get(SPOTIFY_CALL_BASE_URL, headers=header)
        
    return response.json()

def create_access_token(nebula_user_id: int, spotify_user_id: str, display_name: str, expires_delta: timedelta):
    encode = {'sub': spotify_user_id, 'nebula_user_id': nebula_user_id, 'display_name': display_name, 'exp': expires_delta}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials = Depends(security)):
    token = credentials.credentials  # Extract Bearer token string
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        spotify_user_id = payload.get("sub")
        nebula_user_id = payload.get("nebula_user_id")
        display_name = payload.get("display_name")

        if not spotify_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub"
            )

        return {
            "spotify_user_id": spotify_user_id,
            "nebula_user_id": nebula_user_id,
            "display_name": display_name
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/login")
async def login():
    state = secrets.token_urlsafe(16)
    
    query_parameters = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        'scope': 'user-top-read',
        'show_dialog': 'true'
    }
    
    query_string = urlencode(query_parameters)
    auth_url = SPOTIFY_AUTHORIZE_BASE_URL + '/authorize?' + query_string
    
    return RedirectResponse(url=auth_url)

@router.get("/callback/", response_model=Token)
async def callback(code: str):
    body_parameters = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        token_data_response = await client.post(f"{SPOTIFY_AUTHORIZE_BASE_URL}/api/token", 
                                                data=body_parameters, 
                                                headers=TOKEN_REQUEST_HEADERS)
    
    token_data = token_data_response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    
    user_info = await get_user_info(access_token)
    spotify_user_id = user_info.get('id')
    display_name = user_info.get('display_name')
    
    db_session = next(create_db.get_db())
    
    try:
         user = crud.create_nebula_user(db_session, spotify_user_id, display_name)
    except HTTPException as e:
        return {"message": f'{e}'} 
    
    try: 
        crud.update_tokens(db_session, user.id, access_token, refresh_token)
    except HTTPException as e:
        return {"message": f'{e}'} 
    
    token = create_access_token(user.id, user.spotify_user_id, user.display_name, timedelta(minutes=1000))

    return {'access_token': token, 'token_type': 'bearer'}

async def refresh_tokens(user: user_dependency):
    
    db_session = next(create_db.get_db())
    token_model = crud.get_token(db_session, user.get('nebula_user_id'))
    
    body_parameters = {
        'grant_type': 'refresh_token',
        'refresh_token': token_model.refresh_token,
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(f"https://accounts.spotify.com/api/token", data=body_parameters, headers=TOKEN_REQUEST_HEADERS)
    
    token_data = token_response.json()
    new_access_token = token_data.get('access_token')
    new_refresh_token = token_data.get('refresh_token')
    
    crud.update_tokens(db_session, user.get('nebula_user_id'), new_access_token, new_refresh_token)
    
    return token_data

@router.get("/top_100")
async def get_top_100(user: user_dependency):
    nebula_user_id = user.get('nebula_user_id')
    db_session = next(create_db.get_db())
    
    refresh_tokens(user)
    
    token_model = crud.get_token(db_session, nebula_user_id)
    access_token = token_model.access_token
    
    body_parameters = {
        'time_range': 'short_term',
        'limit': 10,
        'offset': 0
    }
    
    header_parameters = {
        'Authorization': f'Bearer {access_token}'
    }
    
    url = "https://api.spotify.com/v1/me/top/tracks"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=body_parameters, headers=header_parameters)
        
    return response.json()
