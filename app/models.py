from pydantic import BaseModel
from typing import list

class Track_Data(BaseModel):
    name: str
    artist: List[str]
    audio_features: Audio_Features


class Audio_Features(BaseModel):
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    loudness: float
    tempo: float

    


