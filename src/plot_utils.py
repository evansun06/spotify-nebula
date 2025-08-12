import plotly.express as px
import pandas as pd
from . import models
import os

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

    filepath = "test_visualizations/projected_tracks.html"
    fig.write_html(filepath)
    print(f"Interactive plot saved to: {filepath}")