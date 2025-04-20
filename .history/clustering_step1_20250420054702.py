### Imports ###
import argparse
import numpy as np
import pandas as pd
import deepgraph as dg
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.cluster import KMeans
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap
import con_sep as cs

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

def plot_families(number_families, fgv, v, plot_title):
    """
    Plot heatwave families or clusters on a map using pcolormesh and Basemap.
    Args:
        number_families (int): Number of families to plot.
        fgv (pd.DataFrame): DataFrame containing family group data.
        v (pd.DataFrame): DataFrame containing node data.
        plot_title (str): Title for the plots.
    """
    cluster_to_season = {0: 'Winter', 1: 'Summer', 2: 'Fall', 3: 'Spring'}

    families = np.arange(number_families)
    for F in families:
        print(f"\nProcessing Family {F}")
        family_data = fgv[fgv['F_kmeans'] == F]

        if family_data.empty:
            print(f"No data found for Family {F}. Skipping...")
            continue

        # Extract data for plotting
        lon = family_data['longitude'].values
        lat = family_data['latitude'].values
        data = family_data['n_cp_nodes'].values

        # Aggregate data to ensure grid consistency
        grid_data = pd.DataFrame({'latitude': lat, 'longitude': lon, 'data': data})
        aggregated_data = grid_data.groupby(['latitude', 'longitude']).mean().reset_index()

        # Extract the aggregated values
        lat = aggregated_data['latitude'].values
        lon = aggregated_data['longitude'].values
        data = aggregated_data['data'].values

        # Create the grid
        lon_grid, lat_grid = np.meshgrid(np.unique(lon), np.unique(lat))

        # Fill missing grid points with zeros
        data_grid = np.full((len(np.unique(lat)), len(np.unique(lon))), 0.0)
        for _, row in aggregated_data.iterrows():
            lat_idx = np.where(np.unique(lat) == row['latitude'])[0][0]
            lon_idx = np.where(np.unique(lon) == row['longitude'])[0][0]
            data_grid[lat_idx, lon_idx] = row['data']

        # Configure map projection using Basemap
        fig, ax = plt.subplots(figsize=(12, 10))
        m = Basemap(projection='cyl', llcrnrlat=lat.min() - 1, urcrnrlat=lat.max() + 1,
                    llcrnrlon=lon.min() - 1, urcrnrlon=lon.max() + 1, resolution='l', ax=ax)

        # Draw coastlines and gridlines
        m.drawcoastlines(linewidth=0.8, color='black')
        m.drawparallels(np.arange(lat.min(), lat.max(), 10), labels=[1, 0, 0, 0], linewidth=0.2, color='gray')
        m.drawmeridians(np.arange(lon.min(), lon.max(), 10), labels=[0, 0, 0, 1], linewidth=0.2, color='gray')

        # Plot data using pcolormesh with reversed color scheme
        pcm = m.pcolormesh(lon_grid, lat_grid, data_grid, cmap='viridis_r', shading='auto', latlon=True)

        # Add colorbar
        cbar = m.colorbar(pcm, location='right', pad="5%")
        cbar.set_label('Number of Heatwaves', fontsize=14)

        # Add title with season name
        season_name = cluster_to_season.get(F, f'Family {F}')
        ax.set_title(f'Family {F} ({season_name})', fontsize=18)

        # Save the plot
        save_path = f'add_your_path_here/{plot_title}_Cluster_{F}_{season_name}.png'  # Replace with your path
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot: {save_path}")
        plt.close(fig)

### Argparser ###

def make_argparser():
    """
    Create argument parser for command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Path to the original dataset to be worked on.", type=str)
    parser.add_argument("-k", "--cluster_number", help="Number of clusters for k-means clustering.", type=int)
    return parser

parser = make_argparser()
args = parser.parse_args()
gv = pd.read_csv(args.data)
k = args.cluster_number
gv['time'] = pd.to_datetime(gv['time'])
g = dg.DeepGraph(gv)

# Create supernodes from deep graph by partitioning the nodes by cp
feature_funcs = {'time': [np.min, np.max],
                 't2m': [np.mean],
                 'magnitude': [np.sum],
                 'latitude': [np.mean],
                 'longitude': [np.mean],
                 't2m': [np.max], 'ytime': [np.mean]}
cpv, ggv = g.partition_nodes('cp', feature_funcs, return_gv=True)

# Append additional features
cpv['g_ids'] = ggv['g_id'].apply(set)
cpv['n_unique_g_ids'] = cpv['g_ids'].apply(len)
cpv['dt'] = cpv['time_amax'] - cpv['time_amin']
cpv['timespan'] = cpv.dt.dt.days + 1
cpv.rename(columns={'magnitude_sum': 'HWMId_magnitude'}, inplace=True)

# Transform day of year values
cpv['doy_cos'] = cpv.ytime_mean.apply(conv_cos)
cpv['doy_sin'] = cpv.ytime_mean.apply(conv_sin)

# Perform k-means clustering
clusterer = KMeans(n_clusters=k, random_state=100)
cluster_labels = clusterer.fit_predict(cpv[['doy_sin', 'doy_cos']])
cpv['kmeans_clust'] = cluster_labels

# Plot k-means clustering
fig, ax = plt.subplots(figsize=(18, 7))
colors = cm.nipy_spectral(cluster_labels.astype(float) / k)
ax.scatter(cpv['doy_cos'], cpv['doy_sin'], marker=".", s=50, lw=0, alpha=0.7, c=colors, edgecolor="k")
ax.set_title(f'k={k}')
ax.set_xlabel('doy_cos')
ax.set_ylabel('doy_sin')
fig.savefig('add_your_path_here/k-means_clustering.png')  # Replace with your path

# Create F_kmeans column
gv['F_kmeans'] = np.ones(len(gv), dtype=int) * -1
gcpv = cpv.groupby('kmeans_clust')
it = gcpv.apply(lambda x: x.index.values)

for F in range(len(it)):
    cp_index = g.v.cp.isin(it.iloc[F])
    g.v.loc[cp_index, 'F_kmeans'] = F

# Plot day of year distribution of clusters
for f in range(k):
    tmp = dg.DeepGraph(g.v)
    tmp.filter_by_values_v('F_kmeans', f)
    plt.hist(tmp.v.ytime, bins=175, label=f'Family {f}', alpha=0.5)
    plt.title("Day of Year Distribution of the Heat Wave Families")
    plt.xlabel('Day of year')
    plt.ylabel('Occurrences')
    plt.legend()
plt.savefig('add_your_path_here/day_of_year_distribution.png')  # Replace with your path

# Plot the families on a map
def n_cp_nodes(cp):
    return len(cp.unique())

feature_funcs = {'magnitude': [np.sum],
                 'latitude': np.min,
                 'longitude': np.min,
                 'cp': n_cp_nodes}

fgv = g.partition_nodes(['F_kmeans', 'g_id'], feature_funcs=feature_funcs)
fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes', 'longitude_amin': 'longitude', 'latitude_amin': 'latitude'}, inplace=True)
fgv['F_kmeans'] = fgv.index.get_level_values('F_kmeans')

plot_families(k, fgv, gv, 'Family')