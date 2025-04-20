### Imports ###
import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import matplotlib.cm as cm

### Functions ###

def conv_sin(doy):
    """
    Convert day of year (DOY) to its sine value.
    Args:
        doy (int): Day of the year.
    Returns:
        float: Sine of the day of the year.
    """
    return np.sin((doy / 365) * 2 * np.pi)

def conv_cos(doy):
    """
    Convert day of year (DOY) to its cosine value.
    Args:
        doy (int): Day of the year.
    Returns:
        float: Cosine of the day of the year.
    """
    return np.cos((doy * 2 * np.pi / 365))

### Main Script ###

# Argument parser
def make_argparser():
    """
    Create argument parser for command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Path to the dataset.", type=str)
    parser.add_argument("-k", "--cluster_number", help="Number of clusters for k-means.", type=int)
    return parser

parser = make_argparser()
args = parser.parse_args()
gv = pd.read_csv(args.data)
k = args.cluster_number
gv['time'] = pd.to_datetime(gv['time'])
g = dg.DeepGraph(gv)

# Feature functions for partitioning
feature_funcs = {
    'time': [np.min, np.max],
    't2m': [np.mean, np.max],
    'magnitude': [np.sum],
    'latitude': [np.mean],
    'longitude': [np.mean],
    'ytime': [np.mean]
}

# Partition graph
cpv, ggv = g.partition_nodes('cp', feature_funcs, return_gv=True)

# Append necessary columns
cpv['g_ids'] = ggv['g_id'].apply(set)  # Geographical ID sets
cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)  # Cardinality of geographical ID sets
cpv['dt'] = cpv['time_amax'] - cpv['time_amin']  # Time spans
cpv['timespan'] = cpv.dt.dt.days + 1  # Duration in days
cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)

# Transform day of year value
cpv['doy_cos'] = cpv.ytime_mean.apply(conv_cos)
cpv['doy_sin'] = cpv.ytime_mean.apply(conv_sin)

# Perform k-means clustering
clusterer = KMeans(n_clusters=k, random_state=100)
cluster_labels = clusterer.fit_predict(cpv[['doy_sin', 'doy_cos']])
cpv['kmeans_clust'] = cluster_labels

# Print cluster centroids
print("Cluster Centroids (doy_sin, doy_cos):")
print(clusterer.cluster_centers_)

# Analyze days of year in each cluster
cluster_to_season = {}
for f in range(k):
    cluster_days = cpv[cpv['kmeans_clust'] == f]['ytime_mean']
    print(f"\nCluster {f} (Number of Days: {len(cluster_days)}):")
    print(cluster_days.values)

    # Map clusters to seasons based on day ranges
    if cluster_days.mean() <= 90:
        cluster_to_season[f] = 'Winter'
    elif cluster_days.mean() <= 180:
        cluster_to_season[f] = 'Spring'
    elif cluster_days.mean() <= 270:
        cluster_to_season[f] = 'Summer'
    else:
        cluster_to_season[f] = 'Autumn'

print("\nCluster to Season Mapping:")
print(cluster_to_season)

# Visualize clusters in circular space
fig, ax = plt.subplots(figsize=(8, 8))
colors = cm.nipy_spectral(cluster_labels.astype(float) / k)
ax.scatter(cpv['doy_cos'], cpv['doy_sin'], c=colors, s=50, alpha=0.7, edgecolor='k')
ax.set_title('Clusters in Circular Space (doy_sin vs. doy_cos)', fontsize=16)
ax.set_xlabel('doy_cos', fontsize=14)
ax.set_ylabel('doy_sin', fontsize=14)
plt.grid(alpha=0.3)
plt.savefig('add_your_path_here/circular_space_clusters.png', dpi=300, bbox_inches='tight')  # Replace with your path
plt.close()

# Plot the day of year distribution of the clusters
season_colors = {'Winter': 'blue', 'Spring': 'red', 'Summer': 'green', 'Autumn': 'orange'}
plt.figure(figsize=(12, 8))
for f in range(k):
    season_name = cluster_to_season[f]
    tmp = dg.DeepGraph(g.v)
    tmp.filter_by_values_v('F_kmeans', f)
    plt.hist(tmp.v.ytime, bins=175, label=season_name, alpha=0.5, color=season_colors[season_name])

plt.title("Day of Year Distribution of the Heat Wave Families", fontsize=16)
plt.xlabel('Day of Year', fontsize=14)
plt.ylabel('Occurrences', fontsize=14)
plt.legend(title="Seasons", fontsize=12, title_fontsize=14)
plt.grid(alpha=0.3)
plt.savefig('add_your_path_here/day_of_year_distribution.png', dpi=300, bbox_inches='tight')  # Replace with your path
plt.close()