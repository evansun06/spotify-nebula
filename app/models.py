from pydantic import BaseModel

class Audio_Features(BaseModel):
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    loudness: float
    tempo: float

class Track_Data(BaseModel):
    name: str
    artist: list
    audio_features: Audio_Features

