from pydantic import BaseModel

class Audio_Features(BaseModel):
    '''Pydantic model for track's audio feautres'''
    
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    loudness: float
    tempo: float
    speechiness:float
    
class Track(BaseModel):
    '''Pydantic model for track'''
    
    name: str
    artist: list
    audio_features: Audio_Features

class Projected_Track(BaseModel):
    '''Pydantic model for projected track used in nebula rendering'''
    
    name: str
    cluster: int
    artist: list
    x: float
    y: float
    z: float
