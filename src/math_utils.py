import numpy as np
from kneed import KneeLocator
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.manifold import TSNE
from . import models 

SEED = 2025


### Main Pipline
### Workflow: Standardize -> Perform KNN / Tune Epsilon -> Apply DBSCAN Clustering -> Project Via TSNE -> Wrap
def pipline(tracklist:list[models.Track]) -> list[models.Projected_Track]:
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

    #4 Project Via TSNE
    tsne = TSNE(n_components=3, perplexity=30, random_state=SEED)
    projection = tsne.fit_transform(matrix_scaled)

    #5 Wrap results
    projected_tracks = [
        models.Projected_Track(
            name=track.name,
            cluster=label,
            artist=track.artist,
            x=coord[0],
            y=coord[1],
            z=coord[2]
        )
        for track, label, coord in zip(tracklist, labels, projection)
    ]

    return projected_tracks


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







    



