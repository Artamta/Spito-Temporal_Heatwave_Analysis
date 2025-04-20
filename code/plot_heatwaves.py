# Module for plotting heatwaves from the dataset

### Imports ###
import numpy as np
import pandas as pd
import deepgraph as dg
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata
import os

# Ensure the output directory exists
OUTPUT_DIR = "add_your_output_directory_here"  # Replace with your desired output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_heatwaves(cpv_path, gv_path, num_heatwaves, sort_by):
    """
    Plot heatwaves from the dataset based on specified criteria.

    Args:
        cpv_path (str): Path to the supernodes table (CPV dataset).
        gv_path (str): Path to the nodes dataset.
        num_heatwaves (int): Number of heatwaves to plot.
        sort_by (str): Column name to sort the heatwaves by.
    """
    # Load datasets
    cpv = pd.read_csv(cpv_path)
    gv = pd.read_csv(gv_path)

    # Sort heatwaves by the specified column
    cpv.sort_values(by=sort_by, inplace=True, ascending=False)

    for i in range(1, num_heatwaves + 1):
        cp = cpv.cp.iloc[i - 1]
        ggg = dg.DeepGraph(gv[gv.cp == cp])
        start = cpv.time_amin.iloc[i - 1]
        end = cpv.time_amax.iloc[i - 1]
        duration = (pd.to_datetime(end) - pd.to_datetime(start)).days + 1
        magnitude = cpv.HWMId_magnitude.iloc[i - 1]

        # Skip unrealistic heatwaves (e.g., duration > 365 days)
        if duration > 365:
            print(f"Skipping Heatwave {i}: Unrealistic duration ({duration} days).")
            continue

        # Define feature functions for partitioning
        def n_cp_nodes(cp):
            return len(cp.unique())

        feature_funcs = {
            'magnitude': [np.sum],
            'latitude': np.min,
            'longitude': np.min,
            'cp': n_cp_nodes
        }
        fgv = ggg.partition_nodes(['g_id'], feature_funcs=feature_funcs)
        fgv.rename(columns={'cp_n_cp_nodes': 'n_cp_nodes', 'longitude_amin': 'longitude', 'latitude_amin': 'latitude'}, inplace=True)

        # Prepare data for plotting
        lon = fgv['longitude'].values
        lat = fgv['latitude'].values
        data = fgv['magnitude_sum'].values

        # Aggregate data to ensure grid consistency
        grid_data = pd.DataFrame({'latitude': lat, 'longitude': lon, 'data': data})
        aggregated_data = grid_data.groupby(['latitude', 'longitude']).mean().reset_index()

        # Extract the aggregated values
        lat = aggregated_data['latitude'].values
        lon = aggregated_data['longitude'].values
        data = aggregated_data['data'].values

        # Create the grid
        lon_grid, lat_grid = np.meshgrid(np.unique(lon), np.unique(lat))

        # Interpolate missing values in the data grid
        points = np.array([aggregated_data['latitude'], aggregated_data['longitude']]).T
        values = aggregated_data['data']
        data_grid = griddata(points, values, (lat_grid, lon_grid), method='linear')

        # Replace any remaining NaN values with 0
        data_grid = np.nan_to_num(data_grid, nan=0.0)

        # Configure map projection
        fig, ax = plt.subplots(figsize=(12, 8))
        m = Basemap(projection='cyl',
                    llcrnrlon=lon.min() - 1, urcrnrlon=lon.max() + 1,
                    llcrnrlat=lat.min() - 1, urcrnrlat=lat.max() + 1,
                    resolution='l', ax=ax)
        m.drawcoastlines(linewidth=0.8, color='black', zorder=10)
        m.drawparallels(range(-50, 50, 20), linewidth=0.2, color='gray', labels=[1, 0, 0, 0], fontsize=10)
        m.drawmeridians(range(0, 360, 20), linewidth=0.2, color='gray', labels=[0, 0, 0, 1], fontsize=10)

        # Plot the data using pcolormesh
        pcm = m.pcolormesh(lon_grid, lat_grid, data_grid, cmap='viridis_r', shading='auto')

        # Add colorbar
        cbar = m.colorbar(pcm, location='right', pad=0.05)
        cbar.set_label('Magnitude (Sum)', fontsize=14)

        # Add title
        ax.set_title(f'Global Heat Wave {i}: {start} to {end}\nDuration: {duration} days, Magnitude: {magnitude:.2f}',
                     fontsize=16, fontweight='bold', pad=20)

        # Save the plot
        save_path = os.path.join(OUTPUT_DIR, f'HWMID_global_{i}.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot: {save_path}")
        plt.close(fig)

