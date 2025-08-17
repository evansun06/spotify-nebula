import base64
from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
import os
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
from src.database import crud, create_db
from jose import JWTError, jwt
from starlette import status
from src import models
import time
import requests
from src import math_utils, plot_utils

'''Load .env'''
load_dotenv()


'''Constants'''
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
RAPID_API_KEY = os.getenv('RAPID_API_KEY')


'''API Router and HTTP bearer'''
router = APIRouter(tags={'spotify'})
security = HTTPBearer()


'''Pydantic Models'''
class Token(BaseModel):
    '''Pydantic model token return'''
    access_token: str
    token_type: str


'''Helper Functions'''
async def get_user_info(access_token: str):
    '''Returns spotify profile for current user'''
    
    header = {"Authorization": f'Bearer {access_token}'}
    async with httpx.AsyncClient() as client:
        response = await client.get(SPOTIFY_CALL_BASE_URL, headers=header)
        
    return response.json()

def create_access_token(nebula_user_id: int, spotify_user_id: str, display_name: str, expires_delta: timedelta):
    '''Creates JWT access token for user with given nebula user ID, spotify user ID, display name, and expirey time'''
    
    encode = {'sub': spotify_user_id, 'nebula_user_id': nebula_user_id, 'display_name': display_name, 'exp': timedelta}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    '''Decodes and parses token to returns dict of nebula user ID, spotify user ID, display name, and expirey time'''
    
    token = credentials.credentials  # Extract Bearer token string
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
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

    except JWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

user_dependency = Annotated[dict, Depends(get_current_user)]

async def refresh_tokens(user: user_dependency):
    '''Refreshes spotify access token and updates SQL database'''
    
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
    if 'refresh_token' in token_data:
        new_refresh_token = token_data['refresh_token']
    else:
        new_refresh_token = token_model.refresh_token
    
    crud.update_tokens(db_session, user.get('nebula_user_id'), new_access_token, new_refresh_token)
    return new_access_token

'''API Endpoints'''
@router.get("/login")
async def login():
    '''Redirects to Spotify Oauth'''
    
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
    '''Creates user, access token, refresh token in SQL database, and returns user info as encoded JWT token'''
    
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


@router.get("/nebula")
async def get_nebula(user: user_dependency):
    '''Parses top 100 tracks from user's spotify to render spotify nebula'''
    
    nebula_user_id = user.get('nebula_user_id')
    
    db_session = next(create_db.get_db())
    if crud.has_expired_token(db_session, nebula_user_id):
        refresh_tokens(user)
    
    token_model = crud.get_token(db_session, nebula_user_id)
    access_token = token_model.access_token
    
    body_parameters = {
        'time_range': 'short_term',
        'limit': 50,
        'offset': 0
    }
    
    header_parameters = {
        'Authorization': f'Bearer {access_token}'
    }
    
    url = "https://api.spotify.com/v1/me/top/tracks"
    
    
    response_1 = requests.get(url, params=body_parameters, headers=header_parameters)
    body_parameters['offset'] = 50
    response_2 = requests.get(url, params=body_parameters, headers=header_parameters)
        
    items_0_to_50 = response_1.json().get('items', [])
    items_50_to_100 = response_2.json().get('items', [])
    
    items = items_0_to_50 + items_50_to_100
    
    tracks = []
    
    for item in items:
        track_name = item.get('name')
        track_artists = []
        track_id = item.get('id')
        print(f"Requesting audio features for track ID: {track_id}")
        
        for artist in item.get('artists'):
            artist_name = artist.get('name')
            track_artists.append(artist_name)
        
        header_parameters = {'x-rapidapi-host': 'track-analysis.p.rapidapi.com',
                             "x-rapidapi-key": RAPID_API_KEY}
        
        rapid_api_url = f"https://track-analysis.p.rapidapi.com/pktx/spotify/{track_id}"
        
        try:
            resp = requests.get(rapid_api_url, headers=header_parameters, timeout=5)
            resp.raise_for_status()
            raw_audio_features = resp.json()

        except requests.exceptions.RequestException as e:
            print(f"RapidAPI request failed for track {track_id}: {e}")
            continue
        
        except ValueError:
            print(f"Invalid JSON from RapidAPI for track {track_id}")
            continue
        
        track_acousticness = raw_audio_features.get('acousticness')
        track_danceability = raw_audio_features.get('danceability')
        track_energy = raw_audio_features.get('energy')
        track_instrumentalness = raw_audio_features.get('instrumentalness')
        track_loudness_str = raw_audio_features.get('loudness')
        track_loudness_str = raw_audio_features.get('loudness')

        if not track_loudness_str:
            print(f"Skipping track {track_id}, no loudness value")
            continue

        track_loudness = float(str(track_loudness_str).replace(" dB", "").strip())
        track_tempo = raw_audio_features.get('tempo')
        track_speechiness = raw_audio_features.get('speechiness')

    
        
        track_audio_features = models.Audio_Features(acousticness=track_acousticness,
                                               danceability=track_danceability,
                                               energy=track_energy,
                                               instrumentalness=track_instrumentalness,
                                               loudness=track_loudness,
                                               tempo=track_tempo,
                                               speechiness=track_speechiness)
        
        track = models.Track(name=track_name, artist=track_artists, audio_features=track_audio_features)
        tracks.append(track)
        print('Track successfully created')
        time.sleep(0.05)

    processed_tracks = math_utils.pipline(tracks)

    plot_utils.visualize_projected_tracks(processed_tracks)
    
    return processed_tracks
