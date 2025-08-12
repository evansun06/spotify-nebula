import base64
from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import os
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
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

SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = HTTPBearer()
router = APIRouter(tags={'auth'})
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/callback')

class Token(BaseModel):
    access_token: str
    token_type: str


def get_user_info(access_token: str):
    url = "https://api.spotify.com/v1/me"
    header = {"Authorization": f'Bearer {access_token}'}
    response = requests.get(url, headers=header)
    return response.json()

def create_access_token(nebula_user_id: int, spotify_user_id: str, display_name: str, expires_delta: timedelta):
    encode = {'sub': spotify_user_id, 'nebula_user_id': nebula_user_id, 'display_name': display_name, 'exp': expires_delta}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        spotify_user_id: str = payload.get('sub')
        nebula_user_id: int = payload.get('nebula_user_id')
        display_name: str = payload.get('display_name')

        return {'spotify_user_id': spotify_user_id, 'nebula_user_id': nebula_user_id, 'display_name': display_name}
    
    except JWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/login")
async def login():
    state = secrets.token_urlsafe(16)
    
    query_parameters = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state
    }
    
    query_string = urlencode(query_parameters)
    auth_url = SPOTIFY_AUTHORIZE_URL + '?' + query_string
    return RedirectResponse(url=auth_url)

@router.post("/callback", response_model=Token)
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
         user = crud.create_nebula_user(db_session, spotify_user_id, display_name)
    except HTTPException as e:
        return {"message": f'{e}'} 
    
    try: 
        crud.update_tokens(db_session, user.id, access_token, refresh_token)
    except HTTPException as e:
        return {"message": f'{e}'} 
    
    token = create_access_token(user.id, user.spotify_user_id, user.display_name, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

@router.get("/top_100")
async def get_top_100(user: user_dependency):
    nebula_user_id = user.get('nebula_user_id')
    db_session = next(create_db.get_db())
    return nebula_user_id