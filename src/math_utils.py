import numpy as np
import umap
from kneed import KneeLocator
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from . import models 
from sklearn.preprocessing import StandardScaler  # Standardizes features
import umap.umap_ as umap  # UMAP for dimensionality reduction
import hdbscan  # HDBSCAN for clustering

SEED = 2025

### Main Pipline
### Workflow: Standardize -> Perform KNN / Tune Epsilon -> Apply DBSCAN Clustering -> Project Via TSNE -> Wrap
def pipline(tracklist: list[models.Track]) -> list[models.Projected_Track]:
    #1 Build Audio Feature Matrix
    feature_matrix = np.array([
        [
            track.audio_features.acousticness,
            track.audio_features.danceability,
            track.audio_features.energy,
            track.audio_features.instrumentalness,
            track.audio_features.loudness,
            track.audio_features.tempo,
            track.audio_features.speechiness
        ]
        for track in tracklist
    ])

    #2 Create Standardizer
    scaler = StandardScaler()  # Standardize each feature to mean=0, std=1
    matrix_scaled = scaler.fit_transform(feature_matrix)  # Apply scaling

    #3 Apply UMAP
    reducer = umap.UMAP(n_components=3, random_state=SEED)  # Create UMAP reducer to 3D space
    projection = reducer.fit_transform(matrix_scaled)  # Project standardized features into 3D

    #4 Apply HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5)  # Create HDBSCAN clusterer, requiring at least 5 points per cluster
    labels = clusterer.fit_predict(projection)  # Assign cluster labels based on density in 3D UMAP space

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
    k = 8
    neighbors = NearestNeighbors(n_neighbors=k)
    neighbors_fit = neighbors.fit(matrix_scaled)
    distances, _ = neighbors_fit.kneighbors(matrix_scaled)
    k_distances = distances[:, k-1]
    k_distances = np.sort(k_distances)


    knee = KneeLocator(
        x=range(len(k_distances)),
        y=k_distances,
        curve="convex",
        direction="increasing"
    )

    if knee.knee is None:
        print("No knee found, using default eps=0.5")
        return 0.5  # fallback
    eps = k_distances[knee.knee]
    print(f"Chosen eps: {eps}")
    return eps








    



