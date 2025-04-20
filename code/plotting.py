# Module for plotting results of heatwave analysis

### Imports ###
import matplotlib.pyplot as plt
import numpy as np
import deepgraph as dg
import os
from scipy.interpolate import griddata
from mpl_toolkits.basemap import Basemap

# Ensure the output directory exists
OUTPUT_DIR = "add_your_output_directory_here"  # Replace with your desired output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_hits(number_families, fgv, v, plot_title):
    """
    Plot heatwave hits on a map using Basemap.
    
    Args:
        number_families (int): Number of heatwave families to plot.
        fgv (pd.DataFrame): DataFrame containing family group data.
        v (pd.DataFrame): DataFrame containing node data.
        plot_title (str): Title for the plots.
    """
    families = np.arange(number_families)
    for F in families:
        gt = dg.DeepGraph(fgv.loc[F])  # Create a DeepGraph instance for each family
        lon, lat = gt.v.longitude.values, gt.v.latitude.values
        data = gt.v.n_nodes.values  # Replace with the appropriate data column

        if len(lon) < 3 or len(lat) < 3:  # Skip if insufficient data
            print(f"Skipping cluster {F + 1} due to insufficient data.")
            continue

        # Create a regular grid for interpolation
        grid_lon = np.linspace(v.longitude.min(), v.longitude.max(), 100)
        grid_lat = np.linspace(v.latitude.min(), v.latitude.max(), 100)
        grid_x, grid_y = np.meshgrid(grid_lon, grid_lat)
        data_grid = griddata((lon, lat), data, (grid_x, grid_y), method='linear')

        # Fill missing values using nearest-neighbor interpolation
        if np.any(np.isnan(data_grid)):
            data_grid = griddata((lon, lat), data, (grid_x, grid_y), method='nearest')

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))
        m = Basemap(projection='cyl', llcrnrlon=grid_lon.min(), urcrnrlon=grid_lon.max(),
                    llcrnrlat=grid_lat.min(), urcrnrlat=grid_lat.max(), resolution='l', ax=ax)
        m.drawcoastlines(linewidth=0.8)
        m.drawparallels(range(-50, 50, 20), linewidth=0.2)
        m.drawmeridians(range(0, 360, 20), linewidth=0.2)

        pcm = m.pcolormesh(grid_lon, grid_lat, data_grid, cmap='viridis_r', shading='auto', latlon=True)
        cbar = m.colorbar(pcm, location='right', pad=0.05)
        cbar.set_label('Number of Heatwave Days', fontsize=15)
        ax.set_title(f'{plot_title} Cluster {F + 1}', fontsize=16)

        # Save the plot
        save_path = os.path.join(OUTPUT_DIR, f'Heatwavedays_{plot_title}_Cluster_{F + 1}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot: {save_path}")
        plt.close(fig)

def plot_families(number_families, fgv, v, plot_title):
    """
    Plot heatwave families on a map using Basemap.
    
    Args:
        number_families (int): Number of heatwave families to plot.
        fgv (pd.DataFrame): DataFrame containing family group data.
        v (pd.DataFrame): DataFrame containing node data.
        plot_title (str): Title for the plots.
    """
    families = np.arange(number_families)
    for F in families:
        gt = dg.DeepGraph(fgv.loc[F])  # Create a DeepGraph instance for each family
        lon, lat = gt.v.longitude.values, gt.v.latitude.values
        data = gt.v.n_cp_nodes.values  # Replace with the appropriate data column

        if len(lon) < 3 or len(lat) < 3:  # Skip if insufficient data
            print(f"Skipping cluster {F + 1} due to insufficient data.")
            continue

        # Create a regular grid for interpolation
        grid_lon = np.linspace(v.longitude.min(), v.longitude.max(), 100)
        grid_lat = np.linspace(v.latitude.min(), v.latitude.max(), 100)
        grid_x, grid_y = np.meshgrid(grid_lon, grid_lat)
        data_grid = griddata((lon, lat), data, (grid_x, grid_y), method='linear')

        # Fill missing values using nearest-neighbor interpolation
        if np.any(np.isnan(data_grid)):
            data_grid = griddata((lon, lat), data, (grid_x, grid_y), method='nearest')

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))
        m = Basemap(projection='cyl', llcrnrlon=grid_lon.min(), urcrnrlon=grid_lon.max(),
                    llcrnrlat=grid_lat.min(), urcrnrlat=grid_lat.max(), resolution='l', ax=ax)
        m.drawcoastlines(linewidth=0.8)
        m.drawparallels(range(-50, 50, 20), linewidth=0.2)
        m.drawmeridians(range(0, 360, 20), linewidth=0.2)

        pcm = m.pcolormesh(grid_lon, grid_lat, data_grid, cmap='viridis_r', shading='auto', latlon=True)
        cbar = m.colorbar(pcm, location='right', pad=0.05)
        cbar.set_label('Number of Heatwaves', fontsize=15)
        ax.set_title(f'{plot_title} Cluster {F + 1}', fontsize=16)

        # Save the plot
        save_path = os.path.join(OUTPUT_DIR, f'{plot_title}_Cluster_{F + 1}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot: {save_path}")
        plt.close(fig)