import plotly.express as px
import pandas as pd
from . import models
import os
import numpy as np
import random
import string
from src.models import Track, Audio_Features  # adjust import path to your code
from . import math_utils

def visualize_projected_tracks(projected_tracks: list[models.Projected_Track], output_folder: str = "track_visualizations", filename: str = "projected_tracks.html"):
    # Convert to DataFrame
    df = pd.DataFrame([{
        "name": track.name,
        "artist": track.artist,
        "cluster": track.cluster,
        "x": track.x,
        "y": track.y,
        "z": track.z
    } for track in projected_tracks])

    fig = px.scatter_3d(
        df,
        x="x", y="y", z="z",
        color="cluster",
        hover_data=["name", "artist"],
        title="Interactive 3D Projection of Tracks"
    )

    fig.show()


def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_artist_list():
    # Just return a list of 1–3 fake artist names
    return [random_string(random.randint(5, 10)) for _ in range(random.randint(1, 3))]

# Define cluster centers for Spotify-like genres
cluster_centers = [
    # acousticness, danceability, energy, instrumentalness, loudness, valence, tempo, speechiness
    [0.2, 0.9, 0.9, 0.1, -5, 0.8, 120, 0.1],  # Pop
    [0.9, 0.4, 0.3, 0.8, -20, 0.6, 90, 0.05], # Acoustic
    [0.1, 0.95, 0.95, 0.05, -3, 0.7, 130, 0.05], # EDM
    [0.3, 0.6, 0.7, 0.1, -6, 0.3, 85, 0.6]    # Rap
]

def generate_feature_dict(center, spread=0.1):
    return {
        "acousticness":      np.clip(np.random.normal(center[0], spread), 0, 1),
        "danceability":      np.clip(np.random.normal(center[1], spread), 0, 1),
        "energy":            np.clip(np.random.normal(center[2], spread), 0, 1),
        "instrumentalness":  np.clip(np.random.normal(center[3], spread), 0, 1),
        "loudness":          np.clip(np.random.normal(center[4], spread * 60), -60, 0),
        "valence":           np.clip(np.random.normal(center[5], spread), 0, 1),
        "tempo":             np.clip(np.random.normal(center[6], spread * 200), 60, 200),
        "speechiness":       np.clip(np.random.normal(center[7], spread), 0, 1)
    }

# Generate 100 clustered tracks
# mock_tracks = [
#     Track(
#         name=f"Song {random_string()}",
#         artist=random_artist_list(),
#         audio_features=Audio_Features(**generate_feature_dict(random.choice(cluster_centers)))
#     )
#     for _ in range(100)
# ]

# visualize_projected_tracks(math_utils.pipline(mock_tracks))
