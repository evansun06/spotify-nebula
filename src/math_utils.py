import numpy as np
from kneed import KneeLocator
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from . import models 

def dbscan(tracklist:list[models.Track]) -> list[models.Clustered_Track]:
    #1 Build Audio Feature Matrix
    feature_matrix = np.array([
        [
            track.audio_features.acousticness,
            track.audio_features.danceability,
            track.audio_features.energy,
            track.audio_features.instrumentalness,
            track.audio_features.loudness,
            track.audio_features.valence,
            track.audio_features.tempo,
            track.audio_features.speechiness
        ]
        for track in tracklist
    ])

    #2 Create Standardizer
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(feature_matrix)

     #3 Apply DBSCAN
    dbscan = DBSCAN(eps=get_esp(matrix_scaled), min_samples=16)
    labels = dbscan.fit_predict(matrix_scaled)

    #4Wrap results
    clustered_tracks = [
        models.Clustered_Track(
            name=track.name,
            artist=track.artist,
            audio_features=track.audio_features,
            cluster=label
        )
        for track, label in zip(tracklist, labels)
    ]

    return clustered_tracks


### Helper function to aquire best epsilon parameter using knee recognizer.
def get_esp(matrix_scaled:np.ndarray) -> float:
    k = 9
    ### Set KNN Model
    neighbors = NearestNeighbors(n_neighbors=k)
    neighbors_fit = neighbors.fit(matrix_scaled)
    distances, _ = neighbors_fit.kneighbors(matrix_scaled)

    ### Aquire the distances for each point between itself and its k neighbor
    k_distances = distances[:, k-1]
    knee = KneeLocator(
        x=range(len(k_distances)),
        y=k_distances,
        curve="convex",
        direction="increasing"
    )
    return k_distances[knee.knee]


