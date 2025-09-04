
import asyncio
import base64
import secrets
import os
import httpx
import time
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from dotenv import load_dotenv
from pydantic import BaseModel
from src.database import crud, create_db
from jose import JWTError, jwt
from starlette import status
from src import models
from src import math_utils, plot_utils
from aiolimiter import AsyncLimiter

'''Load .env'''
load_dotenv()


'''Constants'''
SPOTIFY_AUTHORIZE_BASE_URL = 'https://accounts.spotify.com'
SPOTIFY_CALL_BASE_URL = 'https://api.spotify.com/v1/me'

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
B64_HEADER = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
SPOTIFY_TOKEN_REQUEST_HEADERS = {'Authorization': f'Basic {B64_HEADER}', 'Content-Type': 'application/x-www-form-urlencoded'}
REDIRECT_URI = os.getenv('REDIRECT_URI')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'

RAPID_API_KEY = os.getenv('RAPID_API_KEY')
RAPID_API_HEADERS = {'x-rapidapi-host': 'track-analysis.p.rapidapi.com', 'x-rapidapi-key': RAPID_API_KEY}

'''API Router, HTTP Bearer and Async Limiter'''
router = APIRouter(tags={'spotify'})
security = HTTPBearer()
limiter = AsyncLimiter(10, 1)


'''Pydantic Models'''
class Token(BaseModel):
    '''Pydantic model token return'''
    access_token: str
    token_type: str


'''Helper Functions'''
async def get_user_info(access_token: str):
    '''Returns spotify profile for current user'''
    
    header = {'Authorization': f'Bearer {access_token}'}
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
        spotify_user_id = payload.get('sub')
        nebula_user_id = payload.get('nebula_user_id')
        display_name = payload.get('display_name')

        if not spotify_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token: missing sub'
            )

        return {
            'spotify_user_id': spotify_user_id,
            'nebula_user_id': nebula_user_id,
            'display_name': display_name
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
        token_response = await client.post(f'https://accounts.spotify.com/api/token', data=body_parameters, headers=SPOTIFY_TOKEN_REQUEST_HEADERS)
    
    token_data = token_response.json()
    new_access_token = token_data.get('access_token')
    
    if 'refresh_token' in token_data:
        new_refresh_token = token_data['refresh_token']
    else:
        new_refresh_token = token_model.refresh_token
    
    crud.update_tokens(db_session, user.get('nebula_user_id'), new_access_token, new_refresh_token)
    return new_access_token


async def get_audio_features(track: models.Track):
    '''Gets audio features for a track and returns track, if track does not exist, returns None'''
    
    track_id = track.spotify_id
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'https://track-analysis.p.rapidapi.com/pktx/spotify/{track_id}', headers=RAPID_API_HEADERS, timeout=10)
        
        resp.raise_for_status()
        raw_audio_features = resp.json()
        
        track_acousticness = raw_audio_features.get('acousticness')
        track_danceability = raw_audio_features.get('danceability')
        track_energy = raw_audio_features.get('energy')
        track_instrumentalness = raw_audio_features.get('instrumentalness')
        track_loudness = float(str(raw_audio_features.get('loudness', 0)).replace(' dB', '').strip())
        track_tempo = raw_audio_features.get('tempo')
        track_speechiness = raw_audio_features.get('speechiness')

        track.audio_features = models.Audio_Features(acousticness=track_acousticness,
                                                     danceability=track_danceability,
                                                     energy=track_energy,
                                                     instrumentalness=track_instrumentalness,
                                                     loudness=track_loudness,
                                                     tempo=track_tempo,
                                                     speechiness=track_speechiness)
            
        print(f'Successful for {track.name}')
        return track
        
    except (httpx.HTTPError, ValueError) as e:
        print(f'Failed for track {track.name} e:{e}')
        return None
    
async def limited_get_audio_features(track):
    async with limiter:
        return await get_audio_features(track)

async def get_task_delayed(track, delay):
    await asyncio.sleep(delay)
    return await limited_get_audio_features(track)

'''API Endpoints'''
@router.get('/login')
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

@router.get('/callback/', response_model=Token)
async def callback(code: str):
    '''Creates user, access token, refresh token in SQL database, and returns user info as encoded JWT token'''
    
    body_parameters = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        token_data_response = await client.post(f'{SPOTIFY_AUTHORIZE_BASE_URL}/api/token', 
                                                data=body_parameters, 
                                                headers=SPOTIFY_TOKEN_REQUEST_HEADERS)
    
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
        return {'message': f'{e}'} 
    
    try: 
        crud.update_tokens(db_session, user.id, access_token, refresh_token)
    except HTTPException as e:
        return {'message': f'{e}'} 
    
    token = create_access_token(user.id, user.spotify_user_id, user.display_name, timedelta(minutes=1000))
    frontend_url = f"http://localhost:5173/callback?token={token}"
    
    return RedirectResponse(url=frontend_url)


@router.get('/nebula/{term}')
async def get_nebula(user: user_dependency, term: str):
    '''Parses top 100 tracks from user's Spotify to render Spotify nebula'''

    nebula_user_id = user.get('nebula_user_id')
    db_session = next(create_db.get_db())

    if crud.has_expired_token(db_session, nebula_user_id):
        await refresh_tokens(user)
    
    token_model = crud.get_token(db_session, nebula_user_id)
    access_token = token_model.access_token

    body_parameters = {'time_range': term, 'limit': 50, 'offset': 0}
    header_parameters = {'Authorization': f'Bearer {access_token}'}
    url = f'{SPOTIFY_CALL_BASE_URL}/top/tracks'

    async with httpx.AsyncClient() as client:
        response_1 = await client.get(url, params=body_parameters, headers=header_parameters)
        body_parameters['offset'] = 50
        response_2 = await client.get(url, params=body_parameters, headers=header_parameters)

    items = response_1.json().get('items', []) + response_2.json().get('items', [])

    # Get tracks with no audio features
    tracks_no_af = []

    for item in items:
        
        track_name = item.get('name')
        track_artits = [artist['name'] for artist in item.get('artists', [])]
        track_spotify_id = item.get('id')
        
        track = models.Track(name=track_name,
                             artist=track_artits,
                             spotify_id=track_spotify_id)
        
        tracks_no_af.append(track)
    
    # Get all get_audio_feature coroutines for all tracks
    tasks = []
    
    for i, track in enumerate(tracks_no_af):
        task = get_task_delayed(track, i * 0.15)
        tasks.append(task)

    # Run all tasks concurrently with limit
    tracks_ready = await asyncio.gather(*tasks)

    # ilter out any None results
    tracks = []
    for track in tracks_ready:
        if track is not None:
            tracks.append(track)

    # Process and visualize
    processed_tracks = math_utils.pipline(tracks)

    return processed_tracks
