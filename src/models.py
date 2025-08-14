from pydantic import BaseModel

class Audio_Features(BaseModel):
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    loudness: float
    tempo: float
    speechiness:float
    


class Track(BaseModel):
    name: str
    artist: list
    audio_features: Audio_Features

class Projected_Track(BaseModel):
    name: str
    cluster: int
    artist: list
    x: float
    y: float
    z: float
