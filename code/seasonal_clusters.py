### Imports ###
import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import con_sep as cs
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import os

### Functions ###

# Ensure the output directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Assign seasons based on day of year
def assign_season(doy):
    if 1 <= doy <= 90:
        return 1  # Season 1
    elif 91 <= doy <= 180:
        return 2  # Season 2
    elif 181 <= doy <= 270:
        return 3  # Season 3
    elif 271 <= doy <= 360:
        return 4  # Season 4
    else:
        return np.nan  # Handle invalid days

### Argparser ###

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Give the path to the original dataset to be worked on.",
                        type=str)
    return parser

parser = make_argparser()
args = parser.parse_args()
gv = pd.read_csv(args.data)
gv['time'] = pd.to_datetime(gv['time'])

# Add a day-of-year column
gv['doy'] = gv['time'].dt.dayofyear

# Assign seasons
gv['season'] = gv['doy'].apply(assign_season)

# Perform clustering for each season
output_dir = '/your/dir/..'
ensure_directory_exists(output_dir)

for season in range(1, 5):
    print(f"Processing Season {season}...")
    
    # Filter data for the current season
    season_data = gv[gv['season'] == season]
    
    # Transform day of year value for clustering
    season_data['doy_cos'] = np.cos((season_data['doy'] * 2 * np.pi) / 365)
    season_data['doy_sin'] = np.sin((season_data['doy'] * 2 * np.pi) / 365)
    
    # Perform k-means clustering
    k = 4  # Number of clusters for each season
    clusterer = KMeans(n_clusters=k, random_state=100)
    cluster_labels = clusterer.fit_predict(season_data[['doy_cos', 'doy_sin']])
    season_data['kmeans_clust'] = cluster_labels
    
    # Save the clustering results
    season_data.to_csv(f"{output_dir}season_{season}_clustering.csv", index=False)
    
    # Plot the clustering results
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 6)
    colors = cm.nipy_spectral(cluster_labels.astype(float) / k)
    ax.scatter(season_data['doy_cos'], season_data['doy_sin'], marker=".", s=50, lw=0, alpha=0.7, c=colors, edgecolor="k")
    ax.set_title(f'Season {season} Clustering (k={k})')
    ax.set_xlabel('doy_cos')
    ax.set_ylabel('doy_sin')
    plt.savefig(f"{output_dir}season_{season}_clustering.png")
    plt.close()

print("Seasonal clustering completed!")